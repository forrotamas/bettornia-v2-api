from prometheus_client import Counter

abuse_blocked_total = Counter(
    "abuse_blocked_total",
    "Requests blocked by abuse controls",
    ["reason", "path"],
)
