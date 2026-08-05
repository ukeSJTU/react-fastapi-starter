# Production

Building and running the production-like container stack, verifying it with
Chromium smoke tests, and publishing releases. For local development, see
[`development.md`](development.md).

## Architecture

The full stack uses separate backend and frontend images. Caddy serves the
frontend, handles the SPA fallback, and proxies `/health` and `/api/*` to
FastAPI over the internal Compose network. The stack serves HTTP on port 8080
by default; a deployment platform or an external edge proxy handles TLS.

## Build and run

Create a root Compose environment file and set a URL-safe database password:

```bash
cp .env.example .env
openssl rand -hex 32
```

Place the generated value in `POSTGRES_PASSWORD`. Then build the images, run
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

Open `http://127.0.0.1:8080`. Set `APP_PORT` in the root `.env` file to
publish a different host port. This topology does not publish FastAPI or
PostgreSQL to the host.

The corresponding shortcuts are `just container-build`,
`just container-migrate`, `just container-up`, and `just container-down`.
Neither application startup nor `container-up` ever runs migrations.

The named PostgreSQL volume suits local and single-host validation; it is not
a backup or high-availability strategy. Derived deployments can replace the
bundled database with a managed PostgreSQL service.

## Smoke tests

Run the Chromium smoke tests against a fresh production-like stack:

```bash
just test-e2e
```

This command builds the production images, applies Alembic migrations to an
isolated PostgreSQL volume, starts the stack on a dynamically assigned port,
and removes its temporary containers, images, and volumes when the run
finishes. When not using `just setup`, install the matching Chromium binary
first:

```bash
pnpm exec playwright install chromium
```

For interactive test development, start a stack separately and point the
low-level runner at it:

```bash
PLAYWRIGHT_BASE_URL=http://127.0.0.1:8080 pnpm test:e2e:run -- --headed
```

## Releases

The repository uses one stable SemVer release line. Tags take the form
`vMAJOR.MINOR.PATCH`. Git tags and GitHub Releases are the authoritative
version source; package metadata does not track repository releases.

To publish, open the **Release** workflow in GitHub Actions, choose `main`,
and enter the next version without the `v` prefix. An optional Markdown
summary can precede the generated notes. The workflow publishes the current
`main` commit only after that exact commit passes the complete **CI**
workflow, rejects existing or non-increasing versions, and stops if `main`
advances during the run.

Before publishing the first release, enable GitHub Immutable Releases in the
repository settings. Published tags are never moved, deleted, or reused; ship
a new patch release to correct a faulty one. Releases contain only GitHub's
source archives and generated notes—packages, images, and other build
artifacts are not published.
