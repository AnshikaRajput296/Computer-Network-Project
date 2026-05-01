import requests
import time

url = "http://127.0.0.1:8000/predict"

data = {
    "hour": 8,
    "day": 2,
    "month": 5,
    "temp": 25,
    "weather": 1
}

for i in range(20):
    start = time.time()
    r = requests.post(url, json=data)
    end = time.time()

    print(f"Request {i+1}: {round(end-start,4)} sec")