import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
import joblib

def main():
    df = pd.read_csv("segment_training_data.csv")

    X = df.drop(columns=["label"])
    y = df["label"]

    le = LabelEncoder()
    y_encoded = le.fit_transform(y)

    model = GradientBoostingClassifier()
    model.fit(X, y_encoded)

    joblib.dump(model, "models/segment_classifier.pkl")
    joblib.dump(le, "models/segment_label_encoder.pkl")

    print("✅ Model trained and saved to models/")

if __name__ == "__main__":
    main()


import pandas as pd
import lightgbm as lgb
import joblib
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report

INPUT_CSV = "data/training_data.csv"
MODEL_PATH = "models/segment_classifier.pkl"

def preprocess(df: pd.DataFrame):
    df = df.fillna("")
    categorical = ["record_type", "segment_code", "bank_code", "currency", "tail"]
    for col in categorical:
        df[col] = df[col].astype("category")
    return df

def train():
    df = pd.read_csv(INPUT_CSV)
    df = preprocess(df)

    X = df.drop("label", axis=1)
    y = df["label"]

    X_train, X_test, y_train, y_test = train_test_split(X, y, stratify=y, test_size=0.2, random_state=42)

    model = lgb.LGBMClassifier()
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    print("📊 Classification Report:\n", classification_report(y_test, y_pred))

    joblib.dump(model, MODEL_PATH)
    print(f"✅ Model saved to {MODEL_PATH}")

if __name__ == "__main__":
    train()
