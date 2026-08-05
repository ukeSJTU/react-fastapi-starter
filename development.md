# Development

The day-to-day workflow for working on this repository: installing
dependencies, running PostgreSQL and the apps on the host, and the fast
quality-check loop. For building and running the production-like container
stack and publishing releases, see [`production.md`](production.md). For
package-specific commands, see [`frontend/README.md`](frontend/README.md) and
[`backend/README.md`](backend/README.md).

## Setup

Install both workspaces and the Git hooks:

```bash
just setup
```

The equivalent native commands are in the `Justfile`.

The pre-commit hook formats and lints staged files. The pre-push hook runs
backend and frontend type checks, unit tests that do not require Docker, and
the E2E TypeScript check. Docker-backed integration tests and production
smoke tests stay in the complete checks and in CI.

## Running the stack locally

Start PostgreSQL in Docker:

```bash
docker compose up -d --wait db
```

Compose combines `compose.yaml` with `compose.override.yaml`, so PostgreSQL
binds only to `127.0.0.1:5432`. The database name, user, password, and port
default to local-only values; override them in a root `.env` file (see
`.env.example`).

Configure the backend and apply migrations:

```bash
cp backend/.env.example backend/.env
cd backend
uv run --frozen alembic upgrade head
cd ..
```

Start FastAPI and Vite on the host for fast reloads:

```bash
just dev
```

The frontend runs at `http://127.0.0.1:5173`; FastAPI runs at
`http://127.0.0.1:8000`.

Stop PostgreSQL without deleting its data:

```bash
docker compose down
```

## Quality checks

Run the complete repository checks:

```bash
just check
```

Run backend and frontend tests without the generated-code drift check:

```bash
just test
```

Always run the complete checks before finishing a change. Production smoke
tests run separately; see [`production.md`](production.md).
