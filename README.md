# React + FastAPI Starter

[![CI](https://img.shields.io/github/actions/workflow/status/ukeSJTU/react-fastapi-starter/ci.yml?branch=main&label=CI&logo=githubactions&logoColor=white)](https://github.com/ukeSJTU/react-fastapi-starter/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.14](https://img.shields.io/badge/Python-3.14-3776AB?logo=python&logoColor=white)](backend/README.md)
[![Node 24](https://img.shields.io/badge/Node-24-339933?logo=nodedotjs&logoColor=white)](frontend/README.md)

A modern, business-neutral foundation for React and FastAPI applications: a
starting point for new projects, not a demo of one. The frontend and backend
keep independent dependency, build, test, and deployment boundaries while
sharing coordinated workspace tooling at the repository root.

## Why this template

- **Business-neutral by design.** No auth, users, or CRUD examples baked in —
  add exactly what your project needs, nothing you have to strip out first.
- **One source of truth for the API contract.** FastAPI's OpenAPI schema
  drives Orval-generated TypeScript clients, TanStack Query hooks, Zod
  schemas, and MSW mocks. Both the schema and the generated code are
  committed and checked for drift in CI.
- **A fixed, opinionated stack**, not a menu of options: PostgreSQL +
  SQLAlchemy 2 (async) + Alembic on the backend, TanStack Router/Query/Form
  and Tailwind + shadcn/ui on the frontend. See [`AGENTS.md`](AGENTS.md) for
  the full set of deliberate choices and boundaries.
- **Production-ready from day one.** Separate backend and frontend Docker
  images, a same-origin production stack fronted by Caddy, migrations that
  run only as an explicit step, and Playwright smoke tests against that exact
  stack.
- **A fast local loop.** Vite and FastAPI run on the host with hot reload;
  only PostgreSQL runs in Docker.

## Tech stack

**Backend** — [FastAPI](https://fastapi.tiangolo.com) with Pydantic v2 and
pydantic-settings; [SQLAlchemy 2](https://www.sqlalchemy.org) async +
[psycopg 3](https://www.psycopg.org) + [Alembic](https://alembic.sqlalchemy.org)
on PostgreSQL; [structlog](https://www.structlog.org) for readable local logs
and structured JSON in production; [uv](https://docs.astral.sh/uv/),
[Ruff](https://docs.astral.sh/ruff/), and [mypy](https://mypy-lang.org) for
the toolchain; [pytest](https://docs.pytest.org) and
[Testcontainers](https://testcontainers.com) running tests against real
PostgreSQL.

**Frontend** — [React 19](https://react.dev) with
[TypeScript](https://www.typescriptlang.org) and [Vite](https://vite.dev);
[TanStack Router](https://tanstack.com/router) (file-based),
[Query](https://tanstack.com/query), and [Form](https://tanstack.com/form);
[Tailwind CSS 4](https://tailwindcss.com) and [shadcn/ui](https://ui.shadcn.com)
on [Base UI](https://base-ui.com) primitives; [Orval](https://orval.dev)
generating the typed API client from the OpenAPI schema;
[Vitest](https://vitest.dev), [Testing Library](https://testing-library.com),
and [MSW](https://mswjs.io) for unit and component tests, with
[Playwright](https://playwright.dev) for full-stack smoke tests; formatting
and linting via [Oxc](https://oxc.rs) (Oxfmt, Oxlint).

**Repository** — a coordinated monorepo with independent `frontend/` and
`backend/` packages, a `Justfile` for shared shortcuts, and root-level `e2e/`
Playwright tests; GitHub Actions CI covering backend, frontend, generated-code
drift, and Playwright, plus Dependabot; separate production Dockerfiles and a
full Compose stack behind Caddy.

## Documentation

- [`development.md`](development.md) — local setup and the day-to-day workflow.
- [`production.md`](production.md) — production-like containers and releases.
- [`frontend/README.md`](frontend/README.md) — frontend setup, layout, and quality checks.
- [`backend/README.md`](backend/README.md) — backend setup, layout, and quality checks.

## Requirements

- Python 3.14
- Node.js 24
- uv
- pnpm
- Docker with Docker Compose
- just 1.42 or newer (optional)

## License

MIT — see [`LICENSE`](LICENSE).
