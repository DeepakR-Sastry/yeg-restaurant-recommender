import requests
import random
url = "http://127.0.0.1:8000/recommend"

for i in range(10000):
    rand_lat = random.uniform(53.39, 53.71)
    rand_lon = random.uniform(-113.71, -113.30)
    data = {"lat": rand_lat, "lon" : rand_lon, "k": 10, "radius_m": 1000}

    response = requests.post(url, json=data)

url = "http://127.0.0.1:8000/debug/latencies"
response = requests.get(url)
latencies = response.json()["latencies"]
latencies = latencies[50:]
s = sorted(latencies)
p50 = s[int(0.50 * len(s))]
p99 = s[int(0.99 * len(s))]
p999 = s[int(0.999 * len(s))]
print(min(latencies) * 1000)

print(p50 * 1000)
print(p99 * 1000)
print(p999 * 1000)
print(max(latencies) * 1000)