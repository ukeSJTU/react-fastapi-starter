# syntax=docker/dockerfile:1

FROM python:3.14-slim

COPY --from=ghcr.io/astral-sh/uv:0.10.7 /uv /uvx /bin/

ENV PATH="/app/.venv/bin:$PATH" \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy

WORKDIR /app

COPY pyproject.toml uv.lock .python-version ./
COPY backend/pyproject.toml backend/README.md ./backend/

RUN --mount=type=cache,target=/root/.cache/uv \
    uv sync --frozen --no-dev --no-install-workspace --package backend

RUN groupadd --gid 10001 app \
    && useradd --uid 10001 --gid app --create-home --shell /usr/sbin/nologin app

COPY --chown=app:app backend/alembic.ini ./backend/alembic.ini
COPY --chown=app:app backend/alembic ./backend/alembic
COPY --chown=app:app backend/app ./backend/app

WORKDIR /app/backend

USER app

EXPOSE 8000

HEALTHCHECK --interval=10s --timeout=5s --start-period=10s --retries=5 \
    CMD ["python", "-c", "import urllib.request; response = urllib.request.urlopen('http://127.0.0.1:8000/health', timeout=5); response.close()"]

CMD ["fastapi", "run", "--host", "0.0.0.0", "--port", "8000"]
