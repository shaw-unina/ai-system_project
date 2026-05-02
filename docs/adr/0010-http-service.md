# ADR-0010 — HTTP service: FastAPI + uvicorn, in-URL versioning

**Status:** Accepted
**Date:** 2026-05-02

## Context

Phase 8 needs to expose `RAGFactChecker.verify` over HTTP for the dashboard
(Phase 10) and external scripts. Three real choices:

1. FastAPI + uvicorn (typed Pydantic schemas, OpenAPI, async-first).
2. Flask + gunicorn (simpler but no first-class typing; OpenAPI bolted on).
3. Starlette directly (FastAPI without the magic).

## Decision

**FastAPI + uvicorn**, with the API surface versioned in the URL path
(`/v1/verify`).

Rationale:

- Pydantic is already a hard dep — FastAPI's request/response validation reuses
  the same model machinery and the internal `Verdict` schema, so there's no
  duplicate model maintenance.
- OpenAPI / `/docs` come for free; the dashboard team gets a typed contract
  without us writing a separate spec.
- `def`-handlers run in a worker thread, so the sync `RAGFactChecker.verify`
  doesn't block the event loop. We don't need to make the orchestrator async.

## API versioning: in URL, not header

`/v1/verify` rather than `Accept: application/vnd.misinfo.v1+json`.

Rationale: the service is local-deploy and dashboard-facing; URL versioning is
the easier contract for both `curl` and the dashboard. We can add a v2 by
adding a sibling router without disturbing v1.

## Metrics: in-process, not `prometheus-client`

A ~30-line counter store ([src/misinfo/services/metrics.py](../../src/misinfo/services/metrics.py)) renders the Prometheus text exposition format directly. Phase 9 swaps for the real client when monitoring goes in.

Rationale: keeps the base install slim and avoids a transitive `prometheus-client → wrapt` dependency for Phase 5–7 contributors. The exposition format is stable, so the swap is a drop-in.

## Service is sync; orchestrator stays sync

Endpoints are `def`, not `async def`. Starlette runs sync handlers in its
threadpool. `RAGFactChecker.verify` and the underlying `LanguageModel`
implementations remain sync.

Rationale: avoids a project-wide async refactor for negligible throughput gain
under our latency profile (Groq dominates per-claim time; concurrency comes
from the threadpool).

## Consequences

- One new optional-deps group: `[service]` = `fastapi`, `uvicorn[standard]`,
  `httpx`. Base install stays slim.
- The dashboard (Phase 10) talks to this service over plain HTTP/JSON.
- Phase 9 monitoring can scrape `/metrics` from a real Prometheus. Until then,
  manual inspection via `curl` is the workflow.
- Auth / rate limiting are deferred to Phase 11. The service note in
  `phase-8-decisions.md` flags it as a deploy-only-locally posture.

## Alternatives considered

- **Flask.** Simpler but no first-class type contracts; OpenAPI is ad-hoc.
  Rejected because the dashboard hand-off needs a typed schema and we already
  pay the Pydantic cost.
- **Starlette directly.** Marginal complexity reduction over FastAPI with no
  upside; we lose the dependency-injection plumbing (`Depends(get_factchecker)`).
- **gRPC.** Out of scope; nobody upstream of the service speaks gRPC.
- **`prometheus-client`.** Useful at scale; overkill for Phase 8.
