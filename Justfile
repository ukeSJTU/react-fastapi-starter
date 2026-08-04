set shell := ["bash", "-euo", "pipefail", "-c"]

setup:
    cd backend && uv sync --frozen
    cd frontend && pnpm install --frozen-lockfile
    uv tool install prek
    prek install --prepare-hooks

generate:
    cd backend && uv run python -m scripts.export_openapi
    cd frontend && pnpm generate

check-generated: generate
    git diff --exit-code -- openapi.json frontend/src/api/generated frontend/src/routeTree.gen.ts
    test -z "$(git status --porcelain --untracked-files=all -- openapi.json frontend/src/api/generated frontend/src/routeTree.gen.ts)"

test:
    cd backend && uv run pytest
    cd frontend && pnpm test

check: check-generated
    cd backend && uv run ruff format --check .
    cd backend && uv run ruff check .
    cd backend && uv run mypy app scripts tests
    cd backend && uv run pytest
    cd frontend && pnpm check
