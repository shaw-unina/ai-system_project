# Phase 10 — Decisions

Phase 10 stood up the user-facing dashboard. The decisions below are
captured in detail in their own ADRs; this file is the index.

| # | Decision | Rationale |
|---|---|---|
| ADR-0013 | Next.js 15 App Router + TS strict + Tailwind + React Query + Recharts | Smallest reviewable surface that hits the Phase 2 UI contract; no state-mgmt library needed. |
| ADR-0014 | Browser → Next API route → FastAPI (server-side proxy) | Keeps CORS, secrets, and backend host name off the browser; standard Next pattern. |

## Notable trade-offs

- **No e2e tests this phase.** Vitest unit tests cover the parser,
  components, and localStorage persistence. Playwright lands in Phase
  11 alongside auth and rate-limiting.
- **Hand-written `VerifyResponse` type mirror** in `src/lib/types.ts`
  rather than running `openapi-typescript` in CI. Codegen script is
  committed for local refresh; CI doesn't depend on a live backend.
- **Low-confidence rows in localStorage only.** Honours NFR-Priv-1 (no
  server-side claim persistence) and defers durable storage to Phase
  11 where it gets owner-scoped auth.
- **Polling, not SSE.** 10 s React Query polling on `/metrics` is
  sufficient for an internal dashboard and avoids a backend stream
  endpoint. Polling pauses when the tab is hidden.

## Risks tracked into Phase 11

- Dashboard runs unauthenticated on `localhost:3002`. README + footer
  flag this as local-deploy only.
- Bundle size includes Recharts (~70 KB gzipped) on the operator
  route; the `/verify` route stays under ~110 KB First Load JS.
- Type drift: if FastAPI schemas change, the hand-written TS mirror
  drifts. Mitigation is the committed codegen script; Phase 11 should
  add a CI drift check.
