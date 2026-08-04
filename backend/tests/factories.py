from contextlib import AbstractAsyncContextManager
from typing import Protocol

from fastapi import FastAPI
from httpx import AsyncClient

from app.core.config import Environment, Settings


class AppClientFactory(Protocol):
    def __call__(
        self,
        application: FastAPI,
        *,
        raise_app_exceptions: bool = True,
    ) -> AbstractAsyncContextManager[AsyncClient]: ...


def build_settings(
    *,
    environment: Environment = Environment.TEST,
    database_url: str = "postgresql+psycopg://postgres:postgres@127.0.0.1:1/app",
) -> Settings:
    return Settings.model_validate(
        {
            "environment": environment,
            "log_level": "CRITICAL",
            "database_url": database_url,
            "cors_origins": ["http://localhost:5173"],
            "database_pool_size": 1,
            "database_max_overflow": 0,
            "database_pool_timeout_seconds": 1,
            "database_pool_recycle_seconds": 60,
        }
    )
