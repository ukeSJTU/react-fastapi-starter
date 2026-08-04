from collections.abc import AsyncIterator, Iterator
from contextlib import asynccontextmanager
from pathlib import Path

import pytest
from alembic.config import Config
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import (
    AsyncConnection,
    AsyncSession,
    create_async_engine,
)
from testcontainers.community.postgres import PostgresContainer

from alembic import command
from tests.factories import AppClientFactory

BACKEND_DIR = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="session")
def alembic_config() -> Config:
    config = Config(str(BACKEND_DIR / "alembic.ini"))
    config.set_main_option("script_location", str(BACKEND_DIR / "alembic"))
    return config


@pytest.fixture(scope="session")
def migrated_database_url(alembic_config: Config) -> Iterator[str]:
    with PostgresContainer("postgres:18.4", driver="psycopg") as postgres:
        database_url = postgres.get_connection_url()
        alembic_config.set_main_option("sqlalchemy.url", database_url)
        command.upgrade(alembic_config, "head")
        yield database_url


@pytest.fixture
async def database_connection(
    migrated_database_url: str,
) -> AsyncIterator[AsyncConnection]:
    engine = create_async_engine(migrated_database_url)
    try:
        async with engine.connect() as connection:
            transaction = await connection.begin()
            try:
                yield connection
            finally:
                if transaction.is_active:
                    await transaction.rollback()
    finally:
        await engine.dispose()


@pytest.fixture
async def db_session(
    database_connection: AsyncConnection,
) -> AsyncIterator[AsyncSession]:
    async with AsyncSession(
        bind=database_connection,
        expire_on_commit=False,
        autoflush=False,
        join_transaction_mode="create_savepoint",
    ) as session:
        yield session


@pytest.fixture
def app_client() -> AppClientFactory:
    @asynccontextmanager
    async def create_client(
        application: FastAPI,
        *,
        raise_app_exceptions: bool = True,
    ) -> AsyncIterator[AsyncClient]:
        async with application.router.lifespan_context(application):
            transport = ASGITransport(
                app=application,
                raise_app_exceptions=raise_app_exceptions,
            )
            async with AsyncClient(
                transport=transport,
                base_url="http://test",
            ) as client:
                yield client

    return create_client
