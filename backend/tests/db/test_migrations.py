import pytest
from alembic.config import Config
from alembic.script import ScriptDirectory
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine

pytestmark = pytest.mark.integration


@pytest.mark.asyncio
async def test_alembic_upgrades_empty_postgres_to_current_head(
    migrated_database_url: str,
    alembic_config: Config,
) -> None:
    engine = create_async_engine(migrated_database_url)
    try:
        async with engine.connect() as connection:
            revision_result = await connection.execute(
                text("SELECT version_num FROM alembic_version")
            )

        current_head = ScriptDirectory.from_config(alembic_config).get_current_head()
        assert revision_result.scalar_one() == current_head
    finally:
        await engine.dispose()


@pytest.mark.asyncio
async def test_migrated_template_contains_no_business_tables(
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

        assert list(table_result.scalars()) == ["alembic_version"]
    finally:
        await engine.dispose()
