from fastapi import FastAPI
from schemas import TrafficInput
from utils import classify

import tensorflow as tf
import joblib
import pandas as pd
import numpy as np
import sqlite3
import time
import math

app = FastAPI()

# =====================================================
# Load Model + Scaler
# =====================================================

model = tf.keras.models.load_model(
    "traffic_model_fuzzy.h5",
    custom_objects={"mse": tf.keras.losses.MeanSquaredError()},
    compile=False
)

scaler = joblib.load("scaler.pkl")

# exact training columns
columns = list(scaler.feature_names_in_)

# =====================================================
# SQLite DB
# =====================================================

conn = sqlite3.connect("traffic.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS predictions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    hour INTEGER,
    day INTEGER,
    month INTEGER,
    temp REAL,
    weather TEXT,
    predicted_volume REAL,
    congestion TEXT,
    response_time REAL
)
""")

conn.commit()

# =====================================================
# Home Route
# =====================================================

@app.get("/")
def home():
    return {"message": "Traffic Prediction API Running"}

# =====================================================
# Prediction Route
# =====================================================

@app.post("/predict")
def predict(data: TrafficInput):

    start = time.time()

    # -----------------------------------------
    # Create empty row with all 36 features
    # -----------------------------------------
    row = dict.fromkeys(columns, 0)

    # Numerical values
    row["temp"] = data.temp
    row["rain_1h"] = data.rain_1h
    row["snow_1h"] = data.snow_1h
    row["clouds_all"] = data.clouds_all

    row["hour"] = data.hour
    row["day"] = data.day
    row["month"] = data.month

    # -----------------------------------------
    # Cyclic Features
    # -----------------------------------------
    row["hour_sin"] = math.sin(2 * math.pi * data.hour / 24)
    row["hour_cos"] = math.cos(2 * math.pi * data.hour / 24)

    row["day_sin"] = math.sin(2 * math.pi * data.day / 7)
    row["day_cos"] = math.cos(2 * math.pi * data.day / 7)

    row["month_sin"] = math.sin(2 * math.pi * data.month / 12)
    row["month_cos"] = math.cos(2 * math.pi * data.month / 12)

    # -----------------------------------------
    # Weather One Hot
    # -----------------------------------------
    weather_col = f"weather_main_{data.weather_main}"
    if weather_col in row:
        row[weather_col] = 1

    # -----------------------------------------
    # Holiday One Hot
    # -----------------------------------------
    holiday_col = f"holiday_{data.holiday}"
    if holiday_col in row:
        row[holiday_col] = 1

    # -----------------------------------------
    # Lag Features
    # -----------------------------------------
    row["traffic_lag_1"] = data.traffic_lag_1
    row["traffic_lag_24"] = data.traffic_lag_24

    # -----------------------------------------
    # Convert to DataFrame
    # -----------------------------------------
    df = pd.DataFrame([row], columns=columns)

    # -----------------------------------------
    # Scale
    # -----------------------------------------
    scaled_data = scaler.transform(df)      # shape = (1,36)

    # -----------------------------------------
    # LSTM Input Shape Fix
    # Need (1,24,36)
    # -----------------------------------------
    sequence = np.repeat(scaled_data, 24, axis=0)
    sequence = sequence.reshape(1, 24, 36)

    # -----------------------------------------
    # Prediction
    # -----------------------------------------
    pred = model.predict(sequence, verbose=0)[0][0]

    # -----------------------------------------
    # Fuzzy Classification
    # -----------------------------------------
    congestion = classify(pred)

    # -----------------------------------------
    # Response Time
    # -----------------------------------------
    response_time = round(time.time() - start, 4)

    # -----------------------------------------
    # Save to DB
    # -----------------------------------------
    cursor.execute("""
        INSERT INTO predictions
        (hour, day, month, temp, weather,
         predicted_volume, congestion, response_time)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        data.hour,
        data.day,
        data.month,
        data.temp,
        data.weather_main,
        float(pred),
        congestion,
        response_time
    ))

    conn.commit()

    # -----------------------------------------
    # Return Output
    # -----------------------------------------
    return {
        "predicted_volume": round(float(pred), 2),
        "congestion": congestion,
        "response_time": response_time
    }


@app.get("/")
def home():
    return {"message": "Traffic Prediction API Running"}

# =====================================================
# History Route
# =====================================================

@app.get("/history")
def history():

    cursor.execute("""
        SELECT * FROM predictions
        ORDER BY id DESC
        LIMIT 20
    """)

    rows = cursor.fetchall()

    return {"data": rows}