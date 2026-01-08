from __future__ import annotations
import time
from collections import deque
from dataclasses import dataclass
from typing import Deque, Dict, Tuple
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from app.core.config import settings
from app.abuse.metrics import abuse_blocked_total

@dataclass
class Window:
    ts: Deque[float]

class InMemoryRateLimiter:
    # key: (ip, bucket) -> timestamps
    def __init__(self) -> None:
        self._wins: Dict[Tuple[str, str], Window] = {}

    def allow(self, ip: str, bucket: str, limit_per_min: int) -> bool:
        now = time.time()
        key = (ip, bucket)
        w = self._wins.get(key)
        if w is None:
            w = Window(ts=deque())
            self._wins[key] = w

        # drop older than 60s
        while w.ts and (now - w.ts[0]) > 60.0:
            w.ts.popleft()

        if len(w.ts) >= limit_per_min:
            return False

        w.ts.append(now)
        return True

class InMemoryReplayGuard:
    # key: request_id -> expires_at
    def __init__(self) -> None:
        self._seen: Dict[str, float] = {}

    def check_and_mark(self, rid: str) -> bool:
        # returns True if fresh, False if replay
        now = time.time()
        # prune a bit (simple)
        if len(self._seen) > 50000:
            for k, exp in list(self._seen.items())[:1000]:
                if exp <= now:
                    self._seen.pop(k, None)

        exp = self._seen.get(rid)
        if exp and exp > now:
            return False

        self._seen[rid] = now + settings.replay_ttl_seconds
        return True

_rl = InMemoryRateLimiter()
_rg = InMemoryReplayGuard()

def _client_ip(request: Request) -> str:
    # Prefer X-Forwarded-For first hop if present; otherwise client host.
    xff = request.headers.get("x-forwarded-for")
    if xff:
        return xff.split(",")[0].strip()
    client = request.client
    return client.host if client else "unknown"

def _bucket_for_path(path: str) -> str:
    if path.startswith("/shadow/"):
        return "shadow"
    if path.startswith("/live/"):
        return "live"
    if path.startswith("/settlement/"):
        return "settlement"
    if path.startswith("/reconcile/"):
        return "reconcile"
    return "other"

def _limit_for_bucket(bucket: str) -> int:
    return {
        "shadow": settings.rl_shadow_per_min,
        "live": settings.rl_live_per_min,
        "settlement": settings.rl_settlement_per_min,
        "reconcile": settings.rl_reconcile_per_min,
    }.get(bucket, 120)

class AbuseGuardMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        path = request.url.path

        # Body size limit via Content-Length if present
        cl = request.headers.get("content-length")
        if cl is not None:
            try:
                if int(cl) > settings.max_body_bytes:
                    abuse_blocked_total.labels(reason="body_too_large", path=path).inc()
                    return JSONResponse({"detail": "BODY_TOO_LARGE"}, status_code=413)
            except ValueError:
                pass

        # Rate limit (per IP, per bucket)
        ip = _client_ip(request)
        bucket = _bucket_for_path(path)
        lim = _limit_for_bucket(bucket)
        if not _rl.allow(ip, bucket, lim):
            abuse_blocked_total.labels(reason="rate_limited", path=path).inc()
            return JSONResponse({"detail": "RATE_LIMITED"}, status_code=429)

        # Replay guard for mutating endpoints: require x-request-id and dedupe
        if request.method in ("POST", "PUT", "PATCH", "DELETE"):
            rid = request.headers.get("x-request-id")
            if not rid:
                abuse_blocked_total.labels(reason="missing_request_id", path=path).inc()
                return JSONResponse({"detail": "MISSING_REQUEST_ID"}, status_code=400)
            if not _rg.check_and_mark(rid):
                abuse_blocked_total.labels(reason="replay", path=path).inc()
                return JSONResponse({"detail": "REPLAY_DETECTED"}, status_code=409)

        # For requests without Content-Length, enforce size by reading body once.
        # FastAPI will read it later; we re-inject it into the scope.
        if cl is None and request.method in ("POST", "PUT", "PATCH"):
            body = await request.body()
            if len(body) > settings.max_body_bytes:
                abuse_blocked_total.labels(reason="body_too_large", path=path).inc()
                return JSONResponse({"detail": "BODY_TOO_LARGE"}, status_code=413)

            async def receive() -> dict:
                return {"type": "http.request", "body": body, "more_body": False}
            request._receive = receive  # type: ignore[attr-defined]

        response: Response = await call_next(request)
        return response
