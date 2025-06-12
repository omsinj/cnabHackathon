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
