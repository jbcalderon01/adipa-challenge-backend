from fastapi import FastAPI
from src.health.presentation.health_router import router as health_router

app = FastAPI(title="ADIPA API")

app.include_router(health_router)
