from uuid import UUID

import pytest

from app.main import create_app
from tests.factories import AppClientFactory, build_settings


@pytest.mark.asyncio
async def test_request_without_id_receives_generated_request_id(
    app_client: AppClientFactory,
) -> None:
    application = create_app(build_settings())

    async with app_client(application) as client:
        response = await client.get("/openapi.json")

    assert UUID(response.headers["x-request-id"]).version == 4


@pytest.mark.asyncio
async def test_unsafe_request_id_is_replaced(
    app_client: AppClientFactory,
) -> None:
    application = create_app(build_settings())
    unsafe_request_id = "x" * 129

    async with app_client(application) as client:
        response = await client.get(
            "/openapi.json",
            headers={"x-request-id": unsafe_request_id},
        )

    returned_request_id = response.headers["x-request-id"]
    assert returned_request_id != unsafe_request_id
    assert UUID(returned_request_id).version == 4
