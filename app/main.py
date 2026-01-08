from fastapi import FastAPI
from app.api.routes import router as core_router
from app.api.live_routes import router as live_router
from app.api.settlement_routes import router as settlement_router
from app.api.reconcile_routes import router as reconcile_router
from app.api.metrics_routes import router as metrics_router
from app.adapters.bootstrap import bootstrap_adapters
from app.obs.middleware import ObservabilityMiddleware
from app.obs.metrics import app_info
from app.core.config import settings
import os

app = FastAPI(title="Bettornia v2 execution API (shadow-first)")

bootstrap_adapters()

app.add_middleware(ObservabilityMiddleware)

# Build info metric
service = "bettornia-v2-api"
version = os.getenv("APP_VERSION", "dev")
app_info.labels(service=service, version=version).set(1)

app.include_router(core_router)
app.include_router(live_router)
app.include_router(settlement_router)
app.include_router(reconcile_router)
app.include_router(metrics_router)
