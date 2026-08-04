# Backend

Production-ready, business-neutral FastAPI and PostgreSQL backend foundation.

## Requirements

- Python 3.14
- uv
- PostgreSQL
- Docker for the Testcontainers integration tests

Python dependencies are part of the uv workspace at the repository root. The
workspace owns the shared `.venv`, `.python-version`, and `uv.lock`, while this
directory keeps the backend package metadata and tool configuration.

## Setup

From the repository root, `just setup` installs both workspaces and the Git
hooks. To set up and run only the backend, use the native commands from this
directory after PostgreSQL is running:

```bash
cp .env.example .env
uv sync --frozen
uv run alembic upgrade head
uv run fastapi dev
```

From the repository root, `docker compose up -d --wait db` starts the local
PostgreSQL service on `127.0.0.1:5432`. The root README documents the separate
production-like backend and frontend images and the explicit containerized
migration workflow.

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
For a fast TDD loop that excludes Docker-backed integration tests, run
`uv run pytest -m "not integration"`. Always run the complete suite before
finishing a change.

## Export OpenAPI

Export the schema directly from the application without starting an HTTP server:

```bash
uv run python -m scripts.export_openapi
```

The command always writes the committed contract to `../openapi.json`. The
resulting file is the input to the frontend Orval generator.

From the repository root, `just dev` starts the backend and frontend in
parallel. `just generate` exports the contract and then runs the frontend
generator. `just check-generated` additionally fails when the committed
contract or generated client is stale.
