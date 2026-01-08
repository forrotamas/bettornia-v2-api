from __future__ import annotations
import time
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from app.obs.metrics import http_requests_total, http_request_duration_seconds, http_exceptions_total

def _route_path(request: Request) -> str:
    # Normalized route template when available (prevents label explosion)
    route = request.scope.get("route")
    path = getattr(route, "path", None)
    if path:
        return path
    return request.url.path

class ObservabilityMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        rid = request.headers.get("x-request-id") or str(uuid.uuid4())
        request.state.request_id = rid

        method = request.method
        path = _route_path(request)

        start = time.perf_counter()
        try:
            response: Response = await call_next(request)
        except Exception:
            http_exceptions_total.labels(method=method, path=path).inc()
            raise
        finally:
            dur = time.perf_counter() - start
            http_request_duration_seconds.labels(method=method, path=path).observe(dur)

        http_requests_total.labels(method=method, path=path, status=str(response.status_code)).inc()
        response.headers["x-request-id"] = rid
        return response
