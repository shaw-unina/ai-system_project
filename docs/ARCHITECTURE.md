# Architecture

One-page system overview. For decision-by-decision rationale see
[adr/](adr/).

## Block diagram

```
                      ┌────────────────────┐
   browser ──HTTPS──▶ │  Next.js (3002)    │
                      │  - /verify         │
                      │  - /operator       │  cookie gate
                      │  - /api/* proxy    │  bearer-key inject
                      └─────────┬──────────┘
                                │ http (internal network)
                                ▼
                      ┌────────────────────┐
                      │  FastAPI (8000)    │
                      │  /v1/verify        │  bearer-auth + rate-limit
                      │  /v1/batch         │
                      │  /metrics          │  optional metrics token
                      │  /healthz /readyz  │
                      └─────────┬──────────┘
                                │
        ┌───────────────────────┼───────────────────────┐
        ▼                       ▼                       ▼
  ┌───────────┐           ┌───────────┐           ┌───────────┐
  │ Decompose │ ──────▶  │ Retrieve  │ ──────▶  │ Verify +  │
  │ (LLM)     │           │ BM25 +    │           │ Aggregate │
  │           │           │ dense     │           │ (LLM)     │
  └───────────┘           └───────────┘           └─────┬─────┘
                                                        │
                                                  ┌─────▼─────┐
                                                  │ Abstention│
                                                  │ head + τ  │
                                                  └─────┬─────┘
                                                        ▼
                                              ┌───────────────────┐
                                              │ VerifyResponse    │
                                              │ + low_confidence  │
                                              │ + AI disclosure   │
                                              └───────────────────┘
```

## Module map

| Module | Path | Phase |
|---|---|---|
| Schemas / contract | [src/misinfo/schemas.py](../src/misinfo/schemas.py), [src/misinfo/services/schemas.py](../src/misinfo/services/schemas.py) | 4, 8 |
| Decomposer (LLM) | [src/misinfo/decompose/](../src/misinfo/decompose/) | 5 |
| Retrieval (BM25 + dense hybrid) | [src/misinfo/retrieve/](../src/misinfo/retrieve/) | 5 |
| Verifier / Aggregator (LLM) | [src/misinfo/verify/](../src/misinfo/verify/) | 5, 6 |
| Abstention head + τ selection | [src/misinfo/abstention/](../src/misinfo/abstention/) | 6 |
| Pipeline orchestrator | [src/misinfo/pipeline/](../src/misinfo/pipeline/) | 5 |
| Evaluation harness | [src/misinfo/eval/](../src/misinfo/eval/) | 7 |
| HTTP service | [src/misinfo/services/](../src/misinfo/services/) | 8, 11 |
| Metrics + monitoring | [src/misinfo/services/metrics.py](../src/misinfo/services/metrics.py), [monitoring/](../monitoring/) | 9 |
| Frontend dashboard | [frontend/](../frontend/) | 10, 11 |

## Decision records

ADR-0001 .. ADR-0012 cover Phases 0–9; ADR-0013, ADR-0014 cover Phase 10;
ADR-0015, ADR-0016 cover Phase 11. Index in [adr/README.md](adr/README.md).

## Data flow boundaries (where validation happens)

1. **HTTP edge** (FastAPI): bearer-token auth, per-key rate limit, Pydantic
   schema validation (`max_length=4000`, `extra="forbid"`).
2. **LLM boundary** (`verify/safety.py`): user content sanitized + wrapped in
   a labelled fence; refusal patterns map to `Abstain`.
3. **Output edge** (`VerifyResponse`): `disclosure="ai_generated"` is a
   literal type, `low_confidence` is computed server-side, request_id is
   echoed for tracing (NFR-Trans-2).
