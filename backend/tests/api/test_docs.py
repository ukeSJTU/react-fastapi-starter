import pytest

from app.core.config import Environment
from app.main import create_app
from tests.factories import AppClientFactory, build_settings


@pytest.mark.asyncio
@pytest.mark.parametrize("environment", [Environment.DEVELOPMENT, Environment.TEST])
async def test_docs_and_openapi_are_available_outside_production(
    environment: Environment,
    app_client: AppClientFactory,
) -> None:
    application = create_app(build_settings(environment=environment))

    async with app_client(application) as client:
        docs_response = await client.get("/docs")
        openapi_response = await client.get("/openapi.json")

    assert docs_response.status_code == 200
    assert "scalar" in docs_response.text.lower()
    assert openapi_response.status_code == 200
    assert openapi_response.json()["info"]["title"] == "Backend API"


@pytest.mark.asyncio
async def test_docs_and_openapi_are_not_mounted_in_production(
    app_client: AppClientFactory,
) -> None:
    application = create_app(build_settings(environment=Environment.PRODUCTION))

    async with app_client(application) as client:
        docs_response = await client.get("/docs")
        openapi_response = await client.get("/openapi.json")

    assert docs_response.status_code == 404
    assert openapi_response.status_code == 404
    assert application.openapi_url is None
