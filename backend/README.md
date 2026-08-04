# Backend

Production-ready, business-neutral FastAPI and PostgreSQL backend foundation.

## Requirements

- Python 3.14
- uv
- PostgreSQL
- Docker for the Testcontainers integration tests

## Setup

```bash
cp .env.example .env
uv sync
uv run alembic upgrade head
uv run fastapi dev
```

The API is served at `http://127.0.0.1:8000`. Scalar API documentation is
available at `/docs` in development and test environments. Documentation and
the OpenAPI HTTP route are not mounted in production.

Database migrations are always explicit. Application startup never applies
migrations or creates database objects.

## Quality checks

```bash
uv run ruff format --check .
uv run ruff check .
uv run mypy app tests
uv run pytest
```

The test suite starts a real PostgreSQL container and applies Alembic migrations.

## Export OpenAPI

Export the schema directly from the application without starting an HTTP server:

```bash
uv run python -m app.scripts.export_openapi --output openapi.json
```

The resulting file is suitable as the input to Orval.
