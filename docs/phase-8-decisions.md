# Phase 8 — Decisions

ADR-style summary of what landed in Phase 8. The full plan is in
[phase-8-service.md](phase-8-service.md); the binding ADR is
[adr/0010-http-service.md](adr/0010-http-service.md).

## D-801. FastAPI + uvicorn, sync handlers

See ADR-0010. Sync `def` handlers + Starlette threadpool keeps
`RAGFactChecker.verify` synchronous.

## D-802. Versioned in URL (`/v1/...`)

See ADR-0010. Adding a v2 in the future is a sibling router; the dashboard
sees an explicit `v1` it can pin.

## D-803. API schemas distinct from internal `Verdict`

`VerifyResponse` adds `disclosure`, `low_confidence`, `request_id`,
`latency_ms` on top of the internal contract. Internal-vs-external schema
separation lets the API surface evolve (e.g. add `model_card_url`) without
touching the pipeline.

## D-804. FR-8 in the orchestrator, not the API layer

The "Abstained: <reasons>" rationale is built where the τ override lives, so
the CLI path and the HTTP path emit the same string. No duplication.

## D-805. NFR-Priv-1 default-redact

`MISINFO_LOG_CLAIMS=false` is the default. Logs see `<redacted len=N sha8=…>`.
The opt-in is explicit and per-deployment, not a flag the operator may flip
inadvertently.

## D-806. In-process metrics, no Prometheus client

~30-line store renders the Prometheus exposition format. Phase 9 swaps for
`prometheus-client` when real monitoring goes in. The endpoint contract
(`/metrics` text/plain) doesn't change.

## D-807. `[service]` is an optional dep group

The base install + Phase 5–7 tests don't need `fastapi` / `uvicorn` / `httpx`.
API tests skip cleanly when the extras aren't installed
(`pytest.importorskip("fastapi")`).

## D-808. Pluggable FactChecker via module-level setter

`services.deps.set_factchecker_factory(fn)` overrides the dependency for tests.
`get_factchecker` is `lru_cache`d, so all requests in a process share one
instance and reset between tests via the test fixture.

## D-809. Probe shipped, NFR-Lat-1 reading deferred

Same posture as Phase 7: build the harness, validate offline, defer the
real-backend reading. The probe + microbench test confirms the harness
produces a sane `LatencyReport`; the real numbers go into a follow-up update
to [phase-8-service.md §Real-run procedure](phase-8-service.md).

## D-810. Auth deferred to Phase 11

Local-deploy only. The compose stack binds `0.0.0.0:8000` for convenience;
production deployment is out of scope until the hardening phase.

## Coverage at Phase 8 close

`pytest` → **112 passed, 1 deselected** (live). The new `services/` package
ships with 8 test files exercising every endpoint, the redaction switch, and
the probe.
