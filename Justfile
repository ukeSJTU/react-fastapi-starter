# Requires just 1.42 or newer for parallel recipes.
set shell := ["bash", "-euo", "pipefail", "-c"]

setup:
    uv sync --all-packages --frozen
    pnpm install --frozen-lockfile
    uv run --frozen prek install --prepare-hooks

[parallel]
dev: _dev-backend _dev-frontend

[private]
[working-directory: "backend"]
_dev-backend:
    uv run --frozen fastapi dev

[private]
[working-directory: "frontend"]
_dev-frontend:
    pnpm dev

generate: _export-openapi
    pnpm --filter frontend generate

[private]
[working-directory: "backend"]
_export-openapi:
    uv run --frozen python -m scripts.export_openapi

check-generated: generate
    git diff --exit-code -- openapi.json frontend/src/api/generated frontend/src/routeTree.gen.ts
    test -z "$(git status --porcelain --untracked-files=all -- openapi.json frontend/src/api/generated frontend/src/routeTree.gen.ts)"

[parallel]
test: _test-backend _test-frontend

[private]
[working-directory: "backend"]
_test-backend:
    uv run --frozen pytest

[private]
[working-directory: "frontend"]
_test-frontend:
    pnpm test

check: check-generated && _check-code

[private]
[parallel]
_check-code: _check-backend _check-frontend

[private]
[working-directory: "backend"]
_check-backend:
    uv run --frozen ruff format --check .
    uv run --frozen ruff check .
    uv run --frozen mypy app scripts tests
    uv run --frozen pytest

[private]
[working-directory: "frontend"]
_check-frontend:
    pnpm check

[working-directory: "frontend"]
build:
    pnpm build
