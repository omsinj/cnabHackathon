# anomaly_detector.py
from sklearn.ensemble import IsolationForest
import numpy as np

# Train and return the model (you can move this offline in practice)
def train_anomaly_model():
    # Simulated data: Normally distributed payments with one outlier
    amounts = [1000, 1100, 1200, 1300, 1150, 1500, 98000]  # last is anomaly
    X = np.array(amounts).reshape(-1, 1)

    model = IsolationForest(contamination=0.15, random_state=42)
    model.fit(X)
    return model

# Apply the model to parsed CNAB segments
def detect_anomalies(parsed_data, model):
    anomalies = []
    for batch_idx, batch in enumerate(parsed_data.get("batches", [])):
        for seg_idx, segment in enumerate(batch.get("segments", [])):
            fields = segment.get("fields", {})
            try:
                amt = float(fields.get("payment_amount", "").strip())
                pred = model.predict([[amt]])[0]
                if pred == -1:
                    anomalies.append({
                        "batch": batch_idx + 1,
                        "segment_index": seg_idx + 1,
                        "amount": amt,
                        "segment_type": segment.get("segment_type"),
                        "raw": segment.get("raw"),
                        "message": f"Unusual payment amount: BRL {amt:,.2f}"
                    })
            except Exception:
                continue  # skip malformed entries
    return anomalies
