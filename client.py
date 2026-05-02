import requests

url = "http://127.0.0.1:8000/predict"

data = {
    "temp": 25,
    "rain_1h": 0,
    "snow_1h": 0,
    "clouds_all": 40,
    "hour": 8,
    "day": 2,
    "month": 5,
    "weather_main": "Clouds",
    "holiday": "None",
    "traffic_lag_1": 4200,
    "traffic_lag_24": 3900
}

response = requests.post(url, json=data)

print("Status Code:", response.status_code)
print("Response:", response.json())