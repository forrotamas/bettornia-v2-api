from __future__ import annotations
from prometheus_client import Counter, Histogram, Gauge

# Labels: method, path, status
http_requests_total = Counter(
    "http_requests_total",
    "Total HTTP requests",
    ["method", "path", "status"],
)

http_request_duration_seconds = Histogram(
    "http_request_duration_seconds",
    "HTTP request latency in seconds",
    ["method", "path"],
    buckets=(0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1.0, 2.5, 5.0, 10.0),
)

http_exceptions_total = Counter(
    "http_exceptions_total",
    "Total unhandled exceptions",
    ["method", "path"],
)

app_info = Gauge(
    "app_info",
    "Build/runtime info",
    ["service", "version"],
)
