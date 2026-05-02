# Phase 8 — Service Layer & Local Deployment

**Status:** Implemented
**Reads:** [phase-2/REQUIREMENTS.md](phase-2/REQUIREMENTS.md), [adr/0010-http-service.md](adr/0010-http-service.md)
**Read by:** Phase 9 (monitoring), Phase 10 (dashboard)

## What Phase 8 ships

A versioned FastAPI service over the in-process `RAGFactChecker`, plus Docker
Compose wiring + a Makefile + a latency probe. The full HTTP surface is in
[api.md](api.md); this doc explains the design decisions and which Phase 2
requirements come due here.

```
                        +----------------+
HTTP request  ---->     |  FastAPI app   |
                        |  /v1/verify    |
                        |  /v1/batch     |
                        |  /healthz etc. |
                        +-------+--------+
                                |
                                v
                   +-----------------------------+
                   |   RAGFactChecker.verify     |
                   |   (sync, threadpool-backed) |
                   +-----------------------------+
```

## Requirements satisfied

| ID | What changes in Phase 8 |
|---|---|
| **FR-5** | `POST /v1/verify` returns the same contract as `RAGFactChecker.verify`, plus `disclosure`, `low_confidence`, `request_id`, `latency_ms`. |
| **FR-8** | Orchestrator now records *why* it abstained: `"Abstained: confidence below threshold; retrieval coverage low; …"`. Both CLI and HTTP paths see it. |
| **NFR-Trans-2** | Every response carries `disclosure: "ai_generated"` and a `low_confidence` flag. |
| **NFR-Priv-1** | `MISINFO_LOG_CLAIMS=false` (default) redacts claim text in access logs. The redacted record carries `len + sha8`. |

NFR-Lat-1 / NFR-Tput thresholds remain *measurable* but *unverified* — they
depend on the real Groq backend, which is the same deferred-real-run posture
as Phase 7. The probe in `misinfo.services.probe.probe_latency` plus the CLI
`misinfo probe` command exists to take that reading.

## Design highlights (see [ADR-0010](adr/0010-http-service.md) for full rationale)

- **FastAPI + uvicorn** with `def` (sync) route handlers; the threadpool
  absorbs the synchronous `RAGFactChecker`.
- **Versioning in the URL** (`/v1/...`); add v2 as a sibling router later.
- **Pluggable FactChecker** via `services.deps.set_factchecker_factory(...)`.
  Tests inject a `MockBackend`-driven instance; the default reuses
  `cli._build_factchecker`.
- **In-process metrics** — no `prometheus-client` dep. Phase 9 swaps.
- **Pydantic v2 API schemas** distinct from the internal `Verdict` so the
  external contract can evolve without churn in pipeline code.
- **Middleware chain:** RequestId → StructuredLog (with redaction). Both
  populate request-scoped state and feed the access log + `/metrics`.

## FR-8: abstain rationale builder

Implemented in [src/misinfo/pipeline/orchestrator.py](../src/misinfo/pipeline/orchestrator.py):

```python
if self._tau is not None and confidence < self._tau:
    label = "Abstain"
    reasons = ["confidence below threshold"]
    if signals.get("evidence_coverage", 1.0) < 0.5:
        reasons.append("retrieval coverage low")
    if signals.get("mean_top1", 1.0) < 0.3:
        reasons.append("evidence weakly relevant")
    rationale = "Abstained: " + "; ".join(reasons) + "."
```

The reasons set is data-driven. Adding new signals (e.g. an NLI-alignment
score in Phase 6 future work) just adds another `if` here.

## CLI

```
misinfo serve --host 0.0.0.0 --port 8000 [--workers N] [--reload]
misinfo probe --url http://localhost:8000 --n 20
```

`serve` is what the Dockerfile's `CMD` invokes. `probe` posts synthetic claims
and prints `{n, errors, mean_ms, p50_ms, p95_ms}` — the harness for an
NFR-Lat-1 reading.

## Docker / Compose

[Dockerfile](../Dockerfile) installs the `[inference,service]` extras into the
conda env, exposes port 8000, ships a `HEALTHCHECK` that hits `/healthz`, and
runs `misinfo serve` as the app user.

[docker-compose.yml](../docker-compose.yml) maps `8000:8000` and adds the same
healthcheck so `docker compose ps` reports `healthy`. The Langfuse stack is
unchanged.

## Tests

8 new test files (18 cases). All offline; gated on `pytest.importorskip("fastapi")` so the suite still passes without the `[service]` extra installed.

| File | Covers |
|---|---|
| `test_api_contract.py` | length cap, missing field, extra field |
| `test_api_verify.py` | happy path, low-confidence flag, X-Request-Id propagation |
| `test_api_abstain_rationale.py` | FR-8 — rationale starts with `"Abstained:"` and lists reasons |
| `test_api_batch.py` | batch returns N results in order; >100 / 0 → 422 |
| `test_api_health.py` | `/healthz`, `/readyz`, `/version` shapes |
| `test_api_metrics.py` | `/metrics` is text/plain and counters increment |
| `test_api_logging.py` | NFR-Priv-1 redaction default; explicit opt-in shows full body |
| `test_api_latency_microbench.py` | `probe_latency` round-trips against the in-process app |

`pytest` → **112 passed, 1 deselected.**

## Real-run procedure (deferred)

Same posture as Phase 7's real run — needs Groq access:

1. Bring Langfuse + the app up: `docker compose up --build`.
2. With `GROQ_API_KEY` in `.env`, hit `/v1/verify` for a few real claims.
3. `misinfo probe --n 50` against the running service to take the
   NFR-Lat-1 / NFR-Tput reading.
4. Update [phase-8-decisions.md](phase-8-decisions.md) §Measured-latency with
   the numbers + Langfuse trace ID for one example call.

## Out of scope (deferred)

- Auth / API keys / rate limiting → Phase 11 hardening. Local-deploy posture until then.
- Real Groq-backed latency reading → separate task.
- Streaming / SSE → Phase 10 dashboard requirement.
- Real Prometheus integration → Phase 9.
- Multi-worker uvicorn tuning → Phase 11.
