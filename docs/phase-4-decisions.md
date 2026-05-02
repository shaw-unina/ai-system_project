# Phase 4 — System Architecture: Decisions

ADR-style summary of what landed in Phase 4. The detailed rationale lives in
[docs/adr/](adr/) (eight ADRs, all `Accepted`).

## Headline decisions

- **Pipeline shape:** decompose → per-question retrieve (hybrid BM25 + BGE-small + RRF) → answer × N → aggregate → abstention head.
- **Inference runtime:** **pluggable** behind `LanguageModel` Protocol. **`GroqBackend` is primary**; `LlamaCppBackend` is a deferred reference path; `MockBackend` is for tests.
- **Verifier:** `llama-3.3-70b-versatile` on Groq (primary), `qwen/qwen-2.5-32b` fallback.
- **Structured output:** Groq JSON-mode + one pydantic-validate retry.
- **Output schema:** frozen in `src/misinfo/schemas.py` (`Verdict`, `EvidenceRef`, `VerdictMetadata`, `SubQuestion`, `QuestionAnswer`, `AggregatorOutput`).
- **Observability:** **self-hosted Langfuse v2** (2 containers in compose) with `@observe()` on every stage; `traced(...)` is a no-op when `LANGFUSE_HOST` is unset.

## Phase 2 amendments

- **NFR-Repro-1** scoped: bit-identical reproducibility on the optional `llama_cpp` backend; on Groq, `Verdict.metadata` carries `(backend, model_id, model_version, seed, temperature, langfuse_trace_id)` and re-runs reproduce within the cross-machine tolerances already in `SUCCESS-CRITERIA.md`.
- **NFR-Priv-1** annotated: under `MISINFO_BACKEND=groq` (default), claim text leaves the box. Scoped to public AVeriTeC v2 claims for the controlled experiment; documented in [ETHICS.md](phase-2/ETHICS.md).

## Files landed

- `src/misinfo/schemas.py` — frozen pydantic models.
- `src/misinfo/observability.py` — `traced(...)` decorator, lazy Langfuse import.
- `src/misinfo/inference/{base,factory,mock_backend,groq_backend,llama_cpp_backend}.py`.
- `src/misinfo/pipeline/{__init__,interfaces}.py` — Protocols only; impls in Phase 5.
- `src/misinfo/{decompose,retrieve,verify,abstention}/__init__.py` — re-exports.
- `docs/adr/{README,0001…0008}.md`.
- `docker-compose.yml` — added `langfuse-server` + `langfuse-db`.
- `pyproject.toml` — new `[inference]` and `[local]` extras.
- `.env.example` — added Groq + Langfuse + backend keys.
- `src/misinfo/config.py` — extended `Settings`.

## Tests added

- `tests/test_schemas.py` — Verdict round-trip, label-enum + range + extras-forbid.
- `tests/test_inference_factory.py` — factory selection, mock determinism, llama_cpp stub raises, groq import is lazy.
- `tests/test_observability.py` — `traced(...)` is offline-clean.

## Verification

`pytest -q` should still pass with no new install (Groq + Langfuse are optional extras).
