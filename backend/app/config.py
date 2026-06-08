"""Application configuration, read from environment variables.

Kept dependency-light on purpose: a small dataclass over os.environ so the app
boots (and /health works) without a database or any external service.
"""
from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    app_name: str = os.environ.get("APP_NAME", "CloudRiskIQ API")
    environment: str = os.environ.get("ENVIRONMENT", "development")
    # Present for later use; /health does NOT connect to the DB so the service
    # stays up even when Postgres is unavailable.
    database_url: str = os.environ.get(
        "DATABASE_URL", "postgresql://cloudriskiq:cloudriskiq@localhost:5432/cloudriskiq"
    )
    cors_origins: str = os.environ.get("CORS_ORIGINS", "http://localhost:3000")


settings = Settings()
