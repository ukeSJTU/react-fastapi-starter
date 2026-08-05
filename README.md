# React + FastAPI Starter

A modern, business-neutral foundation for React and FastAPI applications. The
frontend and backend keep independent dependency, build, test, and deployment
boundaries while sharing coordinated workspace tooling at the repository root.

## Requirements

- Python 3.14
- Node.js 24
- uv
- pnpm
- Docker with Docker Compose
- just 1.42 or newer (optional)

## Setup

Install both workspaces and the Git hooks:

```bash
just setup
```

The equivalent native commands are available in the `Justfile`.

## Local development

Start PostgreSQL in Docker:

```bash
docker compose up -d --wait db
```

Compose automatically combines `compose.yaml` with `compose.override.yaml`, so
PostgreSQL is available only on `127.0.0.1:5432`. The database name, user,
password, and port have local defaults and can be overridden in a root `.env`
file; see `.env.example`.

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

The frontend is available at `http://127.0.0.1:5173`, and FastAPI is available
at `http://127.0.0.1:8000`.

Stop PostgreSQL without deleting its data:

```bash
docker compose down
```

## Production-like containers

The full stack uses separate backend and frontend images. Caddy serves the
frontend, handles the SPA fallback, and proxies `/health` and `/api/*` to
FastAPI over the internal Compose network. The stack serves HTTP on port 8080
by default; a deployment platform or an external edge proxy is responsible for
TLS.

Create a root Compose environment file and set a URL-safe database password:

```bash
cp .env.example .env
openssl rand -hex 32
```

Place the generated value in `POSTGRES_PASSWORD`, then build the images, run
migrations explicitly, and start the stack:

```bash
docker compose \
  -f compose.yaml \
  -f compose.production.yaml \
  --profile tools \
  --parallel 2 \
  build

docker compose \
  -f compose.yaml \
  -f compose.production.yaml \
  run --rm migrate

docker compose \
  -f compose.yaml \
  -f compose.production.yaml \
  up -d --wait
```

Open `http://127.0.0.1:8080`. Set `APP_PORT` in the root `.env` file to publish
a different host port. FastAPI and PostgreSQL are not published to the host in
this topology.

The corresponding shortcuts are `just container-build`,
`just container-migrate`, `just container-up`, and `just container-down`.
Migrations are never run by application startup or by `container-up`.

The named PostgreSQL volume is suitable for local and single-host validation,
but it is not a backup or high-availability strategy. Derived deployments can
replace the bundled database with a managed PostgreSQL service.

## Quality checks

Run the complete repository checks:

```bash
just check
```

Run the backend and frontend tests without generated-code drift checks:

```bash
just test
```

Run the Chromium smoke tests against a fresh production-like stack:

```bash
just test-e2e
```

The E2E command builds the production images, applies Alembic migrations to an
isolated PostgreSQL volume, starts the stack on a dynamically assigned port,
and removes its temporary containers, images, and volumes when the run
finishes. Install the matching Chromium binary with
`pnpm exec playwright install chromium` when not using `just setup`.

For interactive test development, start a stack separately and point the
low-level runner at it:

```bash
PLAYWRIGHT_BASE_URL=http://127.0.0.1:8080 pnpm test:e2e:run -- --headed
```
