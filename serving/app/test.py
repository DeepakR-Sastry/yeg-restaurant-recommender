from time import perf_counter, sleep
import requests
url = "http://127.0.0.1:8000/readyz"
# Start the high-resolution timer
start_time = perf_counter()

for i in range(1000):
    response = requests.get(url)
    print(response.json())
# Code execution block to measure
sleep(1.5) 

# Stop the timer
end_time = perf_counter()

# Compute the elapsed time
elapsed = end_time - start_time
print(f"Executed in {elapsed:.6f} seconds")