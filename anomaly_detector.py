# anomaly_detector.py

import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest
from typing import List, Dict


def extract_anomaly_features(parsed_data: Dict) -> pd.DataFrame:
    """
    Extracts numeric features for anomaly detection from parsed CNAB240 data.
    """
    rows = []
    for batch in parsed_data.get("batches", []):
        for segment in batch.get("segments", []):
            fields = segment.get("fields", {})
            seg_type = segment.get("segment_type", "")
            try:
                amount = float(fields.get("payment_amount", "0"))
            except ValueError:
                amount = 0.0
            row = {
                "segment_type": seg_type,
                "amount": amount,
                "length": len(segment.get("raw", "")),
                "is_digit_ratio": sum(c.isdigit() for c in segment.get("raw", "")) / max(len(segment.get("raw", "")), 1),
            }
            rows.append(row)
    return pd.DataFrame(rows)


def detect_anomalies(parsed_data: Dict, contamination: float = 0.05) -> List[str]:
    """
    Detects anomalies in CNAB240 segments using Isolation Forest.
    """
    df = extract_anomaly_features(parsed_data)
    if df.empty:
        return []

    model = IsolationForest(n_estimators=100, contamination=contamination, random_state=42)
    model.fit(df.drop(columns=["segment_type"]))
    df["anomaly"] = model.predict(df.drop(columns=["segment_type"]))

    alerts = []
    for idx, row in df.iterrows():
        if row["anomaly"] == -1:
            alerts.append(
                f"🚨 Anomaly detected in segment {row['segment_type']} at index {idx} — unusual pattern or amount: BRL {row['amount']:.2f}."
            )
    return alerts
