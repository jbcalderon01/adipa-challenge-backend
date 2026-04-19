import logging

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.health.presentation.health_router import router as health_router
from src.quiz_extraction.presentation.routers.quiz_router import router as quiz_router


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)


app = FastAPI(title="ADIPA API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(quiz_router)