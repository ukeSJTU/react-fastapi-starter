from unittest.mock import AsyncMock, Mock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.dependencies import SessionDep
from app.main import create_app
from tests.factories import AppClientFactory, build_settings


@pytest.mark.asyncio
async def test_session_dependency_rolls_back_and_closes_on_exception(
    app_client: AppClientFactory,
) -> None:
    application = create_app(build_settings())
    session = AsyncMock(spec=AsyncSession)
    application.state.session_factory = Mock(return_value=session)

    @application.get("/failing-test-route", operation_id="failForTest")
    async def failing_route(_: SessionDep) -> None:
        raise RuntimeError("expected test failure")

    async with app_client(application, raise_app_exceptions=False) as client:
        response = await client.get("/failing-test-route")

    assert response.status_code == 500
    session.rollback.assert_awaited_once_with()
    session.close.assert_awaited_once_with()
    session.commit.assert_not_awaited()
