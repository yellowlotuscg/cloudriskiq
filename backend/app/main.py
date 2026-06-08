"""CloudRiskIQ FastAPI application entrypoint.

Run locally:
    uvicorn app.main:app --reload --port 8000
Then:
    curl http://localhost:8000/health   -> {"status": "ok", ...}
"""
from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.config import settings

app = FastAPI(
    title=settings.app_name,
    version=__version__,
    description="Aggregates and scores cloud + endpoint + source-control security findings.",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.cors_origins.split(",") if o.strip()],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["system"])
def health() -> dict:
    """Liveness probe. Intentionally has no external dependencies."""
    return {
        "status": "ok",
        "service": "cloudriskiq-api",
        "version": __version__,
        "environment": settings.environment,
    }


@app.get("/", tags=["system"])
def root() -> dict:
    return {"name": settings.app_name, "version": __version__, "docs": "/docs"}
