from fastapi import FastAPI
from app.api.routes import router

app = FastAPI(title="Bettornia v2 execution API (shadow-first)")
app.include_router(router)
