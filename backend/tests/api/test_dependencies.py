from unittest.mock import AsyncMock, Mock

import pytest
from httpx import ASGITransport, AsyncClient

from app.api.dependencies import SessionDep
from app.main import create_app
from tests.factories import build_settings


@pytest.mark.asyncio
async def test_session_dependency_rolls_back_and_closes_on_exception() -> None:
    application = create_app(build_settings())
    session = AsyncMock()
    application.state.session_factory = Mock(return_value=session)

    @application.get("/failing-test-route", operation_id="failForTest")
    async def failing_route(_: SessionDep) -> None:
        raise RuntimeError("expected test failure")

    transport = ASGITransport(app=application, raise_app_exceptions=False)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/failing-test-route")

    assert response.status_code == 500
    session.rollback.assert_awaited_once_with()
    session.close.assert_awaited_once_with()
    session.commit.assert_not_called()
