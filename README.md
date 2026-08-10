# yeg-restaurant-recommender

A restaurant recommender that serves the model over only a single CPU for 1935 venues in Edmonton. 

## Architecture

<diagram placeholder — Week 3>

## Results

### Latency

Server-in to server-out, measured from the Prometheus middleware
histogram. Single uvicorn worker, container under `--cpus=2 --memory=12g`.
Requests sampled uniformly over the Edmonton bbox (53.40–53.65,
-113.70 to -113.30), `radius_m=1000`, `k=10`.

| QPS | p50 | p99 | p999 | achieved | dropped |
|-----|-----|-----|------|----------|---------|
| sequential | 0.365 ms | 0.580 ms | 0.762 ms | — | — |
| 100 | 0.724 ms | 1.44 ms | 1.95 ms | 100.01/s | 0 |
| 200 | 0.685 ms | 1.40 ms | 4.45 ms | 200.01/s | 0 |
| 400 | 0.667 ms | 1.42 ms | 8.65 ms | 400.00/s | 0 |
| 800 | 0.367 ms | 3.86 ms | 9.72 ms | 800.00/s | 0 |
| 1600 | 0.372 ms | ~25 ms | ~44 ms | 1599.98/s | 0 |

Budget: p99 < 50 ms at 100 QPS. 

Load generator shares the host with the container and competes for the
same 2 CPUs so all the numbers are inflated by some unknown amount.

### Drift detection and recovery

<crater-and-recover plot — Week 4>

## Running it

<placeholder>
