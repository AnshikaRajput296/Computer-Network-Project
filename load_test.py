import requests
import threading
import random

url = "http://127.0.0.1:8000/predict"

success = 0
failed = 0
lock = threading.Lock()   # for thread-safe counter update


def send_request(i):
    global success, failed

    # Different request for every client
    data = {
        "temp": random.randint(15, 40),
        "rain_1h": round(random.uniform(0, 5), 2),
        "snow_1h": round(random.uniform(0, 2), 2),
        "clouds_all": random.randint(0, 100),
        "hour": random.randint(0, 23),
        "day": random.randint(1, 7),
        "month": random.randint(1, 12),
        "weather_main": random.choice(
            ["Clouds", "Clear", "Rain", "Snow", "Mist"]
        ),
        "holiday": random.choice(
            ["None", "Christmas Day", "Labor Day"]
        ),
        "traffic_lag_1": random.randint(1000, 7000),
        "traffic_lag_24": random.randint(1000, 7000)
    }

    try:
        response = requests.post(
            url,
            json=data,
            timeout=60
        )

        with lock:
            if response.status_code == 200:
                print(f"Client {i}: SUCCESS -> {response.json()}")
                success += 1
            else:
                print(f"Client {i}: FAILED {response.status_code}")
                print(response.text)
                failed += 1

    except Exception as e:
        with lock:
            print(f"Client {i}: ERROR {e}")
            failed += 1


threads = []

# 20 clients
for i in range(5):
    t = threading.Thread(target=send_request, args=(i,))
    t.start()
    threads.append(t)

for t in threads:
    t.join()

print("\n====== FINAL RESULT ======")
print("Success:", success)
print("Failed :", failed)