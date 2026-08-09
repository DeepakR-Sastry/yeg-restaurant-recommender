from prometheus_client import Histogram, Gauge
from serving.app.config import LATENCY_BUCKETS

REQUEST_LATENCY = Histogram(
    "yeg_request_latency_seconds",
    "Request latency, server-in to server-out",
    labelnames=("strategy", "status", "path"),
    buckets=LATENCY_BUCKETS,
)

CATALOG_SIZE = Gauge(
    "yeg_catalog_venues",
    "Number of venues in the loaded catalog",
)

CATALOG_INFO = Gauge(
    "yeg_catalog_info",
    "Catalog version currently serving",
    labelnames=("catalog_version",),
)