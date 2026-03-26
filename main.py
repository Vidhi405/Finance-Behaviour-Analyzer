from fastapi import FastAPI
from pydantic import BaseModel
import joblib
import pandas as pd
import numpy as np
import json

app = FastAPI()

# -----------------------------
# LOAD MODELS
# -----------------------------
scaler = joblib.load("models/scaler.pkl")
kmeans = joblib.load("models/kmeans.pkl")
iso_forest = joblib.load("models/isolation_forest.pkl")

# Load feature columns
with open("models/feature_columns.json") as f:
    feature_columns = json.load(f)

# -----------------------------
# INPUT FORMAT
# -----------------------------
class TransactionInput(BaseModel):
    user_id: int
    amount: float
    category: str
    payment_mode: str
    date: str   # "YYYY-MM-DD"


# -----------------------------
# FEATURE ENGINEERING
# -----------------------------
def create_features(data):
    df = pd.DataFrame([data])

    # Normalize inputs
    category_value = data['category'].strip().title()
    payment_value = data['payment_mode'].strip().lower()

    # Convert date
    df['date'] = pd.to_datetime(df['date'])

    # -----------------------------
    # BASIC FEATURES
    # -----------------------------
    df['amount_log'] = np.log1p(df['amount'])

    df['month'] = df['date'].dt.month
    df['day_of_week'] = df['date'].dt.dayofweek
    df['is_weekend'] = df['day_of_week'].isin([5, 6]).astype(int)
    df['is_month_start'] = df['date'].dt.is_month_start.astype(int)
    df['is_month_end'] = df['date'].dt.is_month_end.astype(int)
    df['week_of_month'] = (df['date'].dt.day - 1) // 7 + 1

    # Default user-based features
    df['user_transaction_count'] = 1
    df['user_avg_amount'] = df['amount']
    df['days_since_last'] = 0
    df['is_above_avg'] = 0

    # -----------------------------
    # 🔥 IMPORTANT FIX
    # -----------------------------
    # Convert payment_mode to numeric
    payment_map = {
        "upi": 1,
        "cash": 2,
        "card": 3,
        "netbanking": 4,
        "wallet": 5
    }

    df['payment_mode'] = payment_map.get(payment_value, 0)

    # -----------------------------
    # DUMMY FEATURES
    # -----------------------------
    df[f"cat_{category_value}"] = 1
    df[f"dow_{df['day_of_week'].iloc[0]}"] = 1
    df[f"payment_{payment_value.title()}"] = 1

    # -----------------------------
    # MATCH TRAINING FEATURES
    # -----------------------------
    for col in feature_columns:
        if col not in df.columns:
            df[col] = 0

    df = df[feature_columns]

    # Ensure numeric
    df = df.fillna(0)
    df = df.apply(pd.to_numeric, errors='coerce').fillna(0)

    return df


# -----------------------------
# ROUTES
# -----------------------------
@app.get("/")
def home():
    return {"message": "API running 🚀"}


@app.post("/predict")
def predict(data: TransactionInput):

    df = create_features(data.dict())

    # Scale
    scaled = scaler.transform(df)

    # Predict
    cluster = int(kmeans.predict(scaled)[0])
    anomaly = int(iso_forest.predict(scaled)[0])

    return {
        "cluster": cluster,
        "anomaly": "Yes" if anomaly == -1 else "No"
    }