import requests

url = "http://127.0.0.1:8000/predict"

data = {
    "hour": 8,
    "day": 2,
    "month": 5,
    "temp": 25,
    "weather": 1
}

response = requests.post(url, json=data)

print(response.status_code)
print(response.json())