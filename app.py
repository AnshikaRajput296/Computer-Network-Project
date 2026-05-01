# from fastapi import FastAPI
# from schemas import TrafficInput
# from utils import classify
# import tensorflow as tf

# import joblib
# import numpy as np
# import time
# import sqlite3

# app = FastAPI()
# model = tf.keras.models.load_model(
#     "traffic_model_fuzzy.h5",
#     custom_objects={"mse": tf.keras.losses.MeanSquaredError()},
#     compile=False
# )

# scaler = joblib.load("scaler.pkl")
# conn = sqlite3.connect("traffic.db", check_same_thread=False)
# cursor = conn.cursor()

# @app.post("/predict")
# def predict(data: TrafficInput):
#     start = time.time()

#     features = np.array([[data.hour, data.day, data.month, data.temp, data.weather]])
#     features = scaler.transform(features)

#     pred = model.predict(features)[0][0]
#     congestion = classify(pred)

#     end = time.time()
#     latency = round(end - start, 4)

#     cursor.execute("""
#         INSERT INTO predictions
#         (hour, day, month, temp, weather, predicted_volume, congestion, response_time)
#         VALUES (?, ?, ?, ?, ?, ?, ?, ?)
#     """, (
#         data.hour,
#         data.day,
#         data.month,
#         data.temp,
#         data.weather,
#         float(pred),
#         congestion,
#         latency
#     ))

#     conn.commit()

#     return {
#         "predicted_volume": round(float(pred),2),
#         "congestion": congestion,
#         "response_time": latency
#     }


# @app.get("/")
# def home():
#     return {"message": "Traffic Prediction API Running"}

# @app.get("/history")
# def history():
#     cursor.execute("SELECT * FROM predictions ORDER BY id DESC LIMIT 20")
#     rows = cursor.fetchall()

#     return {"data": rows}

# from fastapi import FastAPI
# from schemas import TrafficInput
# from utils import classify
# import tensorflow as tf
# import joblib
# import pandas as pd
# import numpy as np
# import time
# import sqlite3
# import math

# app = FastAPI()

# # Load model
# model = tf.keras.models.load_model(
#     "traffic_model_fuzzy.h5",
#     custom_objects={"mse": tf.keras.losses.MeanSquaredError()},
#     compile=False
# )

# scaler = joblib.load("scaler.pkl")

# # DB
# conn = sqlite3.connect("traffic.db", check_same_thread=False)
# cursor = conn.cursor()

# # Columns used in training
# columns = [
#     'temp', 'rain_1h', 'snow_1h', 'clouds_all',
#     'hour', 'day', 'month',
#     'hour_sin', 'hour_cos',
#     'day_sin', 'day_cos',
#     'month_sin', 'month_cos',

#     'weather_main_Clouds',
#     'weather_main_Drizzle',
#     'weather_main_Fog',
#     'weather_main_Haze',
#     'weather_main_Mist',
#     'weather_main_Rain',
#     'weather_main_Smoke',
#     'weather_main_Snow',
#     'weather_main_Squall',
#     'weather_main_Thunderstorm',

#     'traffic_lag_1',
#     'traffic_lag_24',

#     'holiday_Christmas Day',
#     'holiday_Columbus Day',
#     'holiday_Independence Day',
#     'holiday_Labor Day',
#     'holiday_Martin Luther King Jr Day',
#     'holiday_Memorial Day',
#     'holiday_New Years Day',
#     'holiday_State Fair',
#     'holiday_Thanksgiving Day',
#     'holiday_Veterans Day',
#     'holiday_Washingtons Birthday'
# ]


# @app.post("/predict")
# def predict(data: TrafficInput):

#     start = time.time()

#     row = dict.fromkeys(columns, 0)

#     # Basic values
#     row["temp"] = data.temp
#     row["rain_1h"] = data.rain_1h
#     row["snow_1h"] = data.snow_1h
#     row["clouds_all"] = data.clouds_all

#     row["hour"] = data.hour
#     row["day"] = data.day
#     row["month"] = data.month

#     # Cyclic features
#     row["hour_sin"] = math.sin(2 * math.pi * data.hour / 24)
#     row["hour_cos"] = math.cos(2 * math.pi * data.hour / 24)

#     row["day_sin"] = math.sin(2 * math.pi * data.day / 7)
#     row["day_cos"] = math.cos(2 * math.pi * data.day / 7)

#     row["month_sin"] = math.sin(2 * math.pi * data.month / 12)
#     row["month_cos"] = math.cos(2 * math.pi * data.month / 12)

#     # Weather one-hot
#     weather_col = f"weather_main_{data.weather_main}"
#     if weather_col in row:
#         row[weather_col] = 1

#     # Holiday one-hot
#     holiday_col = f"holiday_{data.holiday}"
#     if holiday_col in row:
#         row[holiday_col] = 1

#     # Lag features
#     row["traffic_lag_1"] = data.traffic_lag_1
#     row["traffic_lag_24"] = data.traffic_lag_24

#     df = pd.DataFrame([row])

#     scaled = scaler.transform(df)

#     pred = model.predict(scaled, verbose=0)[0][0]

#     congestion = classify(pred)

#     latency = round(time.time() - start, 4)

#     # Save log
#     cursor.execute("""
#         INSERT INTO predictions
#         (hour, day, month, temp, weather, predicted_volume, congestion, response_time)
#         VALUES (?, ?, ?, ?, ?, ?, ?, ?)
#     """, (
#         data.hour,
#         data.day,
#         data.month,
#         data.temp,
#         data.weather_main,
#         float(pred),
#         congestion,
#         latency
#     ))

#     conn.commit()

#     return {
#         "predicted_volume": round(float(pred), 2),
#         "congestion": congestion,
#         "response_time": latency
#     }


# @app.get("/")
# def home():
#     return {"message": "Traffic Prediction API Running"}


# @app.get("/history")
# def history():
#     cursor.execute("SELECT * FROM predictions ORDER BY id DESC LIMIT 20")
#     rows = cursor.fetchall()
#     return {"data": rows}

# app.py

from fastapi import FastAPI
from schemas import TrafficInput
from utils import classify
import tensorflow as tf
import joblib
import pandas as pd
import sqlite3
import time
import math

app = FastAPI()

# -------------------------------
# Load model and scaler
# -------------------------------

model = tf.keras.models.load_model(
    "traffic_model_fuzzy.h5",
    custom_objects={
        "mse": tf.keras.losses.MeanSquaredError()
    },
    compile=False
)

scaler = joblib.load("scaler.pkl")

# -------------------------------
# SQLite connection
# -------------------------------

conn = sqlite3.connect("traffic.db", check_same_thread=False)
cursor = conn.cursor()

# Create table if not exists
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

# -------------------------------
# Exact training columns
# -------------------------------

columns = [
    'temp',
    'rain_1h',
    'snow_1h',
    'clouds_all',

    'hour',
    'day',
    'month',

    'hour_sin',
    'hour_cos',

    'day_sin',
    'day_cos',

    'month_sin',
    'month_cos',

    'weather_main_Clouds',
    'weather_main_Drizzle',
    'weather_main_Fog',
    'weather_main_Haze',
    'weather_main_Mist',
    'weather_main_Rain',
    'weather_main_Smoke',
    'weather_main_Snow',
    'weather_main_Squall',
    'weather_main_Thunderstorm',

    'traffic_lag_1',
    'traffic_lag_24',

    'holiday_None',
    'holiday_Columbus Day',
    'holiday_Independence Day',
    'holiday_Labor Day',
    'holiday_Martin Luther King Jr Day',
    'holiday_Memorial Day',
    'holiday_New Years Day',
    'holiday_State Fair',
    'holiday_Thanksgiving Day',
    'holiday_Veterans Day',
    'holiday_Washingtons Birthday'
]

# -------------------------------
# Home route
# -------------------------------

@app.get("/")
def home():
    return {
        "message": "Traffic Prediction API Running"
    }

# -------------------------------
# Prediction route
# -------------------------------

@app.post("/predict")
def predict(data: TrafficInput):

    start = time.time()

    # initialize all columns with 0
    row = dict.fromkeys(columns, 0)

    # basic values
    row["temp"] = data.temp
    row["rain_1h"] = data.rain_1h
    row["snow_1h"] = data.snow_1h
    row["clouds_all"] = data.clouds_all

    row["hour"] = data.hour
    row["day"] = data.day
    row["month"] = data.month

    # cyclic features
    row["hour_sin"] = math.sin(2 * math.pi * data.hour / 24)
    row["hour_cos"] = math.cos(2 * math.pi * data.hour / 24)

    row["day_sin"] = math.sin(2 * math.pi * data.day / 7)
    row["day_cos"] = math.cos(2 * math.pi * data.day / 7)

    row["month_sin"] = math.sin(2 * math.pi * data.month / 12)
    row["month_cos"] = math.cos(2 * math.pi * data.month / 12)

    # weather one-hot encoding
    weather_col = f"weather_main_{data.weather_main}"
    if weather_col in row:
        row[weather_col] = 1

    # holiday one-hot encoding
    holiday_col = f"holiday_{data.holiday}"
    if holiday_col in row:
        row[holiday_col] = 1

    # lag features
    row["traffic_lag_1"] = data.traffic_lag_1
    row["traffic_lag_24"] = data.traffic_lag_24

    # dataframe
    df = pd.DataFrame([row])

    # scale
    scaled_data = scaler.transform(df)

    # prediction
    pred = model.predict(scaled_data, verbose=0)[0][0]

    # fuzzy classification
    congestion = classify(pred)

    # latency
    response_time = round(time.time() - start, 4)

    # save to database
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

    return {
        "predicted_volume": round(float(pred), 2),
        "congestion": congestion,
        "response_time": response_time
    }

# -------------------------------
# History route
# -------------------------------

@app.get("/")
def home():
    return {"message": "Traffic Prediction API Running"}

@app.get("/history")
def history():
    cursor.execute("""
        SELECT * FROM predictions
        ORDER BY id DESC
        LIMIT 20
    """)

    rows = cursor.fetchall()

    return {
        "data": rows
    }