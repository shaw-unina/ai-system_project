# ADR-0014 — Browser → Next API routes → FastAPI

**Status:** accepted (Phase 10).

## Context

The dashboard could either call the FastAPI service directly from the
browser, or route through Next.js API routes that run server-side and
forward to the backend.

## Decision

The browser only ever talks to the Next.js origin. `/api/verify`,
`/api/metrics`, `/api/reports`, and `/api/reports/[slug]` are
server-side route handlers that read `BACKEND_URL` from the
environment and forward to the FastAPI service.

## Consequences

- **No CORS configuration on the FastAPI side.** Same-origin requests
  only.
- **Backend host stays out of the browser.** In Compose,
  `BACKEND_URL=http://app:8000` resolves on the internal network and
  the browser never sees `app`.
- **Authentication, when added in Phase 11, attaches at the Next
  layer.** The FastAPI service can stay unauthenticated on the
  internal network; the public surface is the dashboard origin.
- **One extra network hop per request.** Acceptable — the proxy is on
  the same node as the Next runtime in the typical deploy.
- The reports route (`/api/reports/[slug]`) reads files directly from
  `reports/` on disk rather than going through the backend, since the
  files are colocated with the deploy and the backend has no
  artefact-serving endpoint.
