import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

from app.main import create_app
from tests.factories import build_settings


@pytest.mark.asyncio
async def test_alembic_migrates_empty_schema_and_health_uses_postgres(
    migrated_database_url: str,
) -> None:
    engine = create_async_engine(migrated_database_url)
    try:
        async with engine.connect() as connection:
            table_result = await connection.execute(
                text(
                    "SELECT tablename FROM pg_catalog.pg_tables "
                    "WHERE schemaname = 'public' ORDER BY tablename"
                )
            )
            revision_result = await connection.execute(
                text("SELECT version_num FROM alembic_version")
            )

        assert list(table_result.scalars()) == ["alembic_version"]
        assert revision_result.scalar_one() == "20260804_0001"
    finally:
        await engine.dispose()

    application = create_app(build_settings(database_url=migrated_database_url))
    transport = ASGITransport(app=application)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        response = await client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}
    await application.state.engine.dispose()
