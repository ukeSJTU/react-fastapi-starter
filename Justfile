set shell := ["bash", "-euo", "pipefail", "-c"]

generate:
    cd backend && uv run python -m scripts.export_openapi
    cd frontend && pnpm generate

check-generated: generate
    git diff --exit-code -- openapi.json frontend/src/api/generated
    test -z "$(git status --porcelain --untracked-files=all -- openapi.json frontend/src/api/generated)"

test:
    cd backend && uv run pytest
    cd frontend && pnpm test

check: check-generated
    cd backend && uv run ruff format --check .
    cd backend && uv run ruff check .
    cd backend && uv run mypy app scripts tests
    cd backend && uv run pytest
    cd frontend && pnpm check
