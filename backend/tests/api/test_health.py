from collections.abc import AsyncIterator
from unittest.mock import AsyncMock

import pytest
from fastapi import FastAPI
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_session
from app.main import create_app
from tests.factories import AppClientFactory, build_settings


def application_with_session(session: AsyncSession) -> FastAPI:
    application = create_app(build_settings())

    async def override_session() -> AsyncIterator[AsyncSession]:
        yield session

    application.dependency_overrides[get_session] = override_session
    return application


@pytest.mark.asyncio
async def test_health_returns_healthy_when_database_responds(
    app_client: AppClientFactory,
) -> None:
    session = AsyncMock(spec=AsyncSession)
    application = application_with_session(session)
    async with app_client(application) as client:
        response = await client.get(
            "/health", headers={"x-request-id": "test-request-id"}
        )

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
    assert response.headers["x-request-id"] == "test-request-id"


@pytest.mark.asyncio
async def test_health_returns_safe_503_when_database_is_unavailable(
    app_client: AppClientFactory,
) -> None:
    session = AsyncMock(spec=AsyncSession)
    session.execute.side_effect = RuntimeError("secret connection details")
    application = application_with_session(session)
    async with app_client(application) as client:
        response = await client.get("/health")

    assert response.status_code == 503
    assert response.json() == {"status": "unavailable"}
    assert "secret" not in response.text
    assert "connection" not in response.text


@pytest.mark.asyncio
@pytest.mark.integration
async def test_health_returns_healthy_with_postgres(
    db_session: AsyncSession,
    app_client: AppClientFactory,
) -> None:
    application = application_with_session(db_session)

    async with app_client(application) as client:
        response = await client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
