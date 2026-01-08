from fastapi import FastAPI
from app.api.routes import router
from app.adapters.bootstrap import bootstrap_adapters

app = FastAPI(title="Bettornia v2 execution API (shadow-first)")

bootstrap_adapters()

app.include_router(router)
