set shell := ["bash", "-euo", "pipefail", "-c"]

generate:
    cd backend && uv run python -m scripts.export_openapi
    cd frontend && pnpm generate

check-generated: generate
    git diff --exit-code -- openapi.json frontend/src/api/generated
