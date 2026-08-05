# Frontend

Business-neutral React and TypeScript foundation for the API served by the
backend package.

## Requirements

- Node.js 24
- pnpm

Frontend dependencies are part of the pnpm workspace at the repository root.
The workspace owns the shared `pnpm-lock.yaml` and `packageManager` version,
while this directory keeps the frontend package manifest and tool
configuration.

## Setup

From the repository root, `just setup` installs both workspaces, the
Playwright Chromium binary, and the Git hooks. To set up and run only the
frontend, use the native commands from this directory after the backend is
running:

```bash
pnpm install --frozen-lockfile
pnpm dev
```

The dev server is available at `http://127.0.0.1:5173`. It proxies `/api/*`
and `/health` to `http://127.0.0.1:8000`, so the backend must already be
running; see `backend/README.md`.

## Quality checks

```bash
pnpm format:check
pnpm lint
pnpm typecheck
pnpm test:coverage
```

These four checks together are `pnpm check`, which also runs in CI. For a
fast TDD loop, run `pnpm test:watch` instead of the full coverage run. Always
run the complete checks before finishing a change.

## Generated API client

`src/api/generated` and `src/routeTree.gen.ts` are generated and committed to
Git. Treat both as read-only: never hand-edit, lint, or format them.

```bash
pnpm generate
```

`pnpm generate:api` runs Orval against the committed `../openapi.json` to
produce Fetch request functions, TanStack Query hooks, Zod schemas, and MSW
mocks in `src/api/generated`. `pnpm generate:routes` runs the TanStack Router
CLI against the file routes in `src/routes` to produce `src/routeTree.gen.ts`.

Regenerate after any backend API change. From the repository root,
`just generate` exports the OpenAPI schema from the backend first, and
`just check-generated` additionally fails when the committed contract or
generated output is stale.

## Source layout

- `src/routes/` — file-based route components (TanStack Router).
- `src/components/`, `src/components/ui/` — reusable UI; `ui/` holds shadcn
  components generated into the repository, which are regular source files
  and safe to edit directly.
- `src/hooks/` — reusable hooks not tied to a single route or component.
- `src/lib/` — framework-agnostic utilities and cross-cutting helpers.
- `src/api/` — the hand-written Fetch setup plus `generated/` (see above).
- `src/app/` — app-wide providers and router wiring.
- `src/test/` — shared Vitest setup and render helpers; individual tests live
  next to the source they cover as `*.test.ts(x)`.

Server state is managed with TanStack Query against the generated hooks; forms
use TanStack Form with Zod validation. Styling is Tailwind CSS 4 with shadcn/ui
components built on Base UI primitives and Lucide icons.

## Testing

Vitest, React Testing Library, and MSW cover units and components. MSW
handlers are generated alongside the API client, so component tests can mock
backend responses without a running server. Coverage reports are written to
`coverage/`.

A small set of full-stack smoke tests lives outside this package in the
repository root `e2e/`, driven by Playwright; see the root `README.md`.
