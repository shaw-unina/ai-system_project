# ADR-0016 — Dashboard password gate on `/operator`

**Status:** accepted (Phase 11).

## Context

Phase 10's operator dashboard exposes live `/metrics` tiles, Phase 7
reports, and the low-confidence cases table. None of that should be on
the public internet without a gate.

## Decision

- A single shared password in `OPERATOR_PASSWORD` gates `/operator/*`.
- Implemented in [frontend/middleware.ts](../../frontend/middleware.ts):
  unauthenticated requests redirect to `/login`, which posts to
  `/api/login` and sets an `httpOnly`, `sameSite=lax`, 8-hour
  `operator_session` cookie.
- `/verify` stays open — it's the demo surface end-users hit.
- Empty `OPERATOR_PASSWORD` disables the gate (local dev).

## Alternatives considered

| Option | Why not |
|---|---|
| OAuth / SSO | Adds a provider dependency and a user model we don't have. Post-1.0. |
| Basic auth via reverse proxy | Pushes a mandatory deploy step (nginx config) onto every operator. |
| Per-user accounts in the app | Out of scope — there are no roles to express. |

## Consequences

- The cookie value is the password itself. Rotation = change
  `OPERATOR_PASSWORD` and force re-login on all sessions.
- 8-hour cookie lifetime balances ergonomics against drift; documented in
  [OPERATOR-GUIDE.md](../OPERATOR-GUIDE.md).
- The middleware also stamps security headers (CSP, X-Frame-Options,
  etc.) on every response — this ADR co-locates them since both are
  edge-of-Next concerns.
