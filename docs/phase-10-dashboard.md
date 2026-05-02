# Phase 10 — Frontend Dashboard

Greenfield Next.js 15 (App Router, TypeScript strict, Tailwind) under
[frontend/](../frontend/). Two surfaces:

- `/verify` — end-user claim submission. Renders `VerdictCard` with
  verdict, confidence, evidence, rationale, low-confidence flag, and a
  permanent AI-disclosure banner (NFR-Trans-2).
- `/operator` — operator dashboard. Three sections: live `/metrics`
  tiles polled every 10 s, Phase 7 report list + inline markdown viewer,
  session-only low-confidence cases table.

## Stack

| Concern | Choice |
|---|---|
| Framework | Next.js 15 App Router |
| Language | TypeScript strict |
| Styling | Tailwind CSS 3.4 |
| Data fetching | TanStack React Query (10 s polling) |
| Charts | Recharts (verdict mix) |
| Markdown | react-markdown + remark-gfm |
| Tests | Vitest + @testing-library/react + jsdom |

## Backend integration

Browser → Next API routes → FastAPI service. The Next routes
(`/api/verify`, `/api/metrics`, `/api/reports`, `/api/reports/[slug]`)
proxy to `${BACKEND_URL}` so the browser never sees the backend host
and CORS stays off the table.

- Local: `BACKEND_URL=http://localhost:8000`
- Compose: `BACKEND_URL=http://app:8000`, dashboard at `localhost:3002`.

## NFR alignment

| NFR | How |
|---|---|
| NFR-Trans-2 | `DisclosureBanner` mounted in `app/layout.tsx`; `VerdictCard` shows a visible low-confidence warning; `Abstain` renders `AbstainCallout` with FR-8 reasons. |
| NFR-Priv-1 | Low-confidence rows live only in `localStorage`; no server-side persistence. |
| NFR-Maint-1 | Frontend lint + typecheck + test + build run as a separate CI job. |

## Verification

```
cd frontend
npm run lint
npm run typecheck
npm run test -- --run
npm run build
```

All four pass on Node 20. Test suite: 13 cases across 5 files.

Compose smoke: `docker compose up --build` brings the dashboard up at
`localhost:3002` once the `app` healthcheck is green.

## Out of scope (deferred to Phase 11)

Authentication, rate limiting, server-side persistence of dashboard
state, Playwright e2e, mobile/responsive polish, brand styling, i18n.
