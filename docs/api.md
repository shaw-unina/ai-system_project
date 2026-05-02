# misinfo HTTP API

The service is a thin FastAPI shell over the in-process `RAGFactChecker`. The
ASGI app lives at [src/misinfo/services/api.py](../src/misinfo/services/api.py).
OpenAPI is auto-served at `/docs` and `/openapi.json`.

## Run

```bash
# Local (no Docker)
misinfo serve --host 127.0.0.1 --port 8000

# Docker Compose (also brings up Langfuse)
docker compose up --build
```

## Endpoints

### `POST /v1/verify`

Single-claim verification.

```bash
curl -X POST localhost:8000/v1/verify \
  -H 'content-type: application/json' \
  -d '{"claim": "Paris is the capital of France."}'
```

Request:

| Field | Type | Notes |
|---|---|---|
| `claim` | string (1–4000) | Required. Per Phase 2 SCOPE. |
| `client_id` | string? | Optional caller identifier. Logged. |

Response (`VerifyResponse`):

| Field | Type | Notes |
|---|---|---|
| `verdict` | `Supported` \| `Refuted` \| `NotEnoughEvidence` \| `Abstain` | |
| `confidence` | float ∈ [0, 1] | Calibrated by the configured abstention head. |
| `evidence` | list of `EvidenceRef` | Deduplicated across sub-questions. |
| `rationale` | string | When `verdict = Abstain`, starts with `"Abstained:"` and lists reasons (FR-8). |
| `metadata` | `VerdictMetadata` | Includes `model_id`, `model_version`, `langfuse_trace_id`, `config_hash`. |
| `disclosure` | `"ai_generated"` | NFR-Trans-2 banner. |
| `low_confidence` | bool | True iff `verdict = Abstain` or `confidence < 0.5`. |
| `request_id` | string | uuid4 (or echoed `X-Request-Id`). Also returned in the response header. |
| `latency_ms` | float | Server-measured. |

Errors:

| Status | Cause |
|---|---|
| 422 | Validation error (missing claim, > 4000 chars, extra fields). Body is `ErrorEnvelope`. |
| 500 | Unhandled error. Body is `ErrorEnvelope` with `request_id`. |

### `POST /v1/batch`

Batch (≤ 100 claims). Body: `{"claims": ["...", "..."]}`. Response:
`{"results": [VerifyResponse, ...]}`. Order preserved.

### `GET /healthz`

Liveness only. Always returns `{"status": "ok"}` if the process is alive. Used by Docker / Compose healthcheck.

### `GET /readyz`

Readiness. Constructs the FactChecker (cached) and returns `{ready, backend, head, tau}`.

### `GET /version`

Returns package and model identifiers — used for run-manifest construction.

### `GET /metrics`

Prometheus text exposition. Counters: `misinfo_requests_total`, `misinfo_verdicts_total`. Histogram: `misinfo_latency_seconds_bucket`. No `prometheus-client` dep — see ADR-0010.

## Privacy (NFR-Priv-1)

Default behaviour: access logs **redact** the request body and log only `<redacted len=N sha8=…>`. To capture full bodies for debugging, set `MISINFO_LOG_CLAIMS=true`. Do not enable in production without an explicit data-handling note.

## Transparency (NFR-Trans-2)

Every `/v1/verify` and `/v1/batch` response carries `disclosure: "ai_generated"` and a `low_confidence` boolean. Phase 10 will surface both in the dashboard.

## Probe

```bash
misinfo probe --url http://localhost:8000 --n 20
```

Posts `n` synthetic claims and prints `{n, errors, mean_ms, p50_ms, p95_ms}`. Used to take a Phase 8 NFR-Lat-1 reading once Groq is wired up.
