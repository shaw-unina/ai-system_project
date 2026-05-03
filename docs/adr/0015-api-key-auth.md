# ADR-0015 — Bearer-token auth + sliding-window rate limit

**Status:** accepted (Phase 11).

## Context

Phase 8 shipped the FastAPI service unauthenticated (suitable for local
dev / on-prem, called out in the README). Phase 11 makes it deploy-safe
without adopting a user model.

## Decision

- **API auth** is a comma-separated allowlist in `MISINFO_API_KEYS`.
  Requests must carry `Authorization: Bearer <key>`. Empty = auth disabled
  (preserves local dev + the existing test suite).
- **Rate limit** is a per-key sliding window over 60 s, configurable via
  `MISINFO_RATE_LIMIT_PER_MIN` (default 60). Implemented in-process in
  [src/misinfo/services/auth.py](../../src/misinfo/services/auth.py).
- `/healthz`, `/readyz`, `/version` stay open. `/metrics` is gated by an
  optional `MISINFO_METRICS_TOKEN`.

## Alternatives considered

| Option | Why not |
|---|---|
| `slowapi` | Adds a dependency for ~30 lines of logic; we don't need its decorator-rich API. |
| OAuth / OIDC | Out of scope for a single-tenant deploy without a user model. |
| Per-IP rate limit | Wrong cardinality — keys are stable identities; IPs aren't. |
| Redis-backed bucket | Premature for single-replica deploys. Documented as a follow-up. |

## Consequences

- Multi-replica deploys multiply the effective quota by replica count
  (each process keeps its own bucket). Documented in
  the relevant ADRs.
- Tests opt out by leaving `MISINFO_API_KEYS` unset.
- The frontend reads `BACKEND_API_KEY` server-side only; the browser
  never sees the bearer token.
