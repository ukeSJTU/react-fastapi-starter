# syntax=docker/dockerfile:1

FROM node:24-bookworm-slim AS build

ENV PNPM_HOME="/pnpm"
ENV PATH="$PNPM_HOME:$PATH"

WORKDIR /app

RUN corepack enable

COPY package.json pnpm-lock.yaml pnpm-workspace.yaml ./
COPY frontend/package.json ./frontend/package.json

RUN --mount=type=cache,target=/pnpm/store \
    pnpm install --frozen-lockfile --filter frontend...

COPY frontend ./frontend

RUN pnpm --filter frontend build

FROM caddy:2.11.4-alpine

COPY frontend/Caddyfile /etc/caddy/Caddyfile
COPY --from=build --chown=65534:65534 /app/frontend/dist /srv

USER 65534:65534

EXPOSE 8080

HEALTHCHECK --interval=10s --timeout=5s --start-period=5s --retries=5 \
    CMD ["curl", "--fail", "--silent", "--show-error", "http://127.0.0.1:8080/"]
