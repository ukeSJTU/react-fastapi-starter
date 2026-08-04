from collections.abc import Iterator
from pathlib import Path

import pytest
from alembic.config import Config
from testcontainers.community.postgres import PostgresContainer
from testcontainers.core.config import testcontainers_config

from alembic import command

BACKEND_DIR = Path(__file__).resolve().parents[1]
testcontainers_config.ryuk_disabled = True


@pytest.fixture(scope="session")
def migrated_database_url() -> Iterator[str]:
    with PostgresContainer("postgres:18.4", driver="psycopg") as postgres:
        database_url = postgres.get_connection_url()
        alembic_config = Config(str(BACKEND_DIR / "alembic.ini"))
        alembic_config.set_main_option("script_location", str(BACKEND_DIR / "alembic"))
        alembic_config.set_main_option("sqlalchemy.url", database_url)
        command.upgrade(alembic_config, "head")
        yield database_url
