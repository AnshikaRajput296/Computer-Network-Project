import streamlit as st
import requests
import pandas as pd

API_URL = "http://127.0.0.1:8000"

st.set_page_config(page_title="Traffic Predictor", layout="centered")

st.title("🚦 Traffic Prediction System")

# =====================================================
# INPUT SECTION (WITH RANGES)
# =====================================================

st.subheader("Enter Traffic Parameters")

temp = st.number_input("Temperature (°C)", min_value=-30.0, max_value=50.0, value=20.0)
rain_1h = st.number_input("Rain (mm last 1h)", min_value=0.0, max_value=100.0, value=0.0)
snow_1h = st.number_input("Snow (mm last 1h)", min_value=0.0, max_value=50.0, value=0.0)
clouds_all = st.slider("Cloud Coverage (%)", 0, 100, 50)


from datetime import time

selected_time = st.time_input("Select Time", value=time(12, 0))

hour = selected_time.hour

day_map = {
    "Sunday": 0,
    "Monday": 1,
    "Tuesday": 2,
    "Wednesday": 3,
    "Thursday": 4,
    "Friday": 5,
    "Saturday": 6
}

day_name = st.selectbox("Day of Week", list(day_map.keys()))
day = day_map[day_name]
month_map = {
    "January": 1, "February": 2, "March": 3,
    "April": 4, "May": 5, "June": 6,
    "July": 7, "August": 8, "September": 9,
    "October": 10, "November": 11, "December": 12
}

month_name = st.selectbox("Month", list(month_map.keys()))
month = month_map[month_name]
weather_main = st.selectbox("Weather Condition", [
    "Clear", "Clouds", "Rain", "Snow", "Mist", "Fog"
])

holiday = st.selectbox("Holiday Type", [
    "None", "Diwali", "Christmas", "NewYear"
])

traffic_lag_1 = st.number_input("Traffic 1 hour ago", min_value=0.0, max_value=100000.0, value=1000.0)
traffic_lag_24 = st.number_input("Traffic 24 hours ago", min_value=0.0, max_value=100000.0, value=1000.0)

# =====================================================
# PREDICTION
# =====================================================

if st.button(" Predict Traffic"):

    payload = {
        "temp": temp,
        "rain_1h": rain_1h,
        "snow_1h": snow_1h,
        "clouds_all": clouds_all,
        "hour": hour,
        "day": day,
        "month": month,
        "weather_main": weather_main,
        "holiday": holiday,
        "traffic_lag_1": traffic_lag_1,
        "traffic_lag_24": traffic_lag_24
    }

    try:
        response = requests.post(f"{API_URL}/predict", json=payload)

        if response.status_code == 200:
            result = response.json()


            
            congestion = result["congestion"]
            st.info(f" Response Time: {result['response_time']} sec")

            if congestion.lower() == "high":
                st.error(f"High Traffic\n\nVolume: {result['predicted_volume']}")
            elif congestion.lower() == "medium":
                st.warning(f"Moderate Traffic\n\nVolume: {result['predicted_volume']}")
            else:
                st.success(f"Low Traffic\n\nVolume: {result['predicted_volume']}")


        else:
            st.error(f"API Error: {response.text}")

    except Exception as e:
        st.error(f"Connection Error: {e}")
import sqlite3
import pandas as pd

st.divider()
st.subheader("Last 20 Predictions")

if st.button("Show History"):

    try:
        conn = sqlite3.connect("traffic.db")
        
        query = """
        SELECT 
            id,
            hour,
            day,
            month,
            temp,
            weather,
            predicted_volume,
            congestion,
            response_time,
            timestamp
        FROM predictions
        ORDER BY id DESC
        LIMIT 20
        """

        df = pd.read_sql_query(query, conn)

        conn.close()

        df["timestamp"] = pd.to_datetime(df["timestamp"])
        df = df.sort_values(by="timestamp", ascending=False)

        st.dataframe(df, width="stretch",hide_index=True)

    except Exception as e:
        st.error(f"Database Error: {e}")