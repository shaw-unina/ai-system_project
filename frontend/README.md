# misinfo · frontend

Next.js 15 dashboard for the misinformation detector. Two views:

- `/verify` — submit a claim, see `VerdictCard` (verdict, confidence, evidence, rationale, AI-generated disclosure, low-confidence flag).
- `/operator` — live `/metrics` tiles, Phase 7 reports browser, low-confidence session list.

## Local dev

Requires Node 20+. From this directory:

```bash
npm install
npm run dev          # http://localhost:3002
```

The Next.js app proxies the FastAPI backend (Phase 8). Start it separately:

```bash
# from repo root
misinfo serve --host 127.0.0.1 --port 8000
```

The proxy reads `BACKEND_URL` (defaults to `http://localhost:8000`).

## Tests / build

```bash
npm run lint
npm run typecheck
npm run test -- --run
npm run build
```

## Type generation

The TS contract for `VerifyResponse` lives in [`src/lib/types.ts`](src/lib/types.ts) (hand-written mirror of the Pydantic schema). To regenerate the full OpenAPI mirror against a running backend:

```bash
npm run codegen:types       # writes openapi-types/api.ts
```

## Docker

`docker-compose.yml` at the repo root runs the dashboard at `localhost:3002`:

```bash
docker compose up --build
```

## Limitations

- **No auth, no rate limiting.** Local-deploy only — Phase 11 lands hardening.
- Low-confidence session table uses `localStorage`; nothing is persisted server-side.
- `react-markdown` only — no MDX, no scripts in reports.
