import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .routers.charts import downloads_router

app = FastAPI()


def _cors_allow_origins() -> list[str]:
    raw = os.getenv("CORS_ALLOW_ORIGINS", "")
    return [origin.strip() for origin in raw.split(",") if origin.strip()]


if allow_origins := _cors_allow_origins():
    app.add_middleware(
        CORSMiddleware,
        allow_origins=allow_origins,
        allow_credentials=True,
        allow_methods=["GET"],
        allow_headers=["Authorization", "Content-Type"],
    )

app.include_router(downloads_router)
