from collections.abc import AsyncIterator
from unittest.mock import AsyncMock

import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import get_session
from app.main import create_app
from tests.factories import build_settings


def application_with_session(session: AsyncSession) -> FastAPI:
    application = create_app(build_settings())

    async def override_session() -> AsyncIterator[AsyncSession]:
        yield session

    application.dependency_overrides[get_session] = override_session
    return application


@pytest.mark.asyncio
async def test_health_returns_healthy_when_database_responds() -> None:
    session = AsyncMock(spec=AsyncSession)
    application = application_with_session(session)
    transport = ASGITransport(app=application)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get(
            "/health", headers={"x-request-id": "test-request-id"}
        )

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
    assert response.headers["x-request-id"] == "test-request-id"
    session.execute.assert_awaited_once()


@pytest.mark.asyncio
async def test_health_returns_safe_503_when_database_is_unavailable() -> None:
    session = AsyncMock(spec=AsyncSession)
    session.execute.side_effect = RuntimeError("secret connection details")
    application = application_with_session(session)
    transport = ASGITransport(app=application)

    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")

    assert response.status_code == 503
    assert response.json() == {"status": "unavailable"}
    assert "secret" not in response.text
    assert "connection" not in response.text
