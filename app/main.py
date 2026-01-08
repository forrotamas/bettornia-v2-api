from fastapi import FastAPI
from app.api.routes import router as core_router
from app.api.live_routes import router as live_router
from app.adapters.bootstrap import bootstrap_adapters

app = FastAPI(title="Bettornia v2 execution API (shadow-first)")

# Deterministic boot (no import side-effects)
bootstrap_adapters()

# Routes
app.include_router(core_router)
app.include_router(live_router)
