# Phase 5 — Baseline Implementation: Decisions

Short ADR-style summary of the choices that landed in Phase 5. The Phase 5 plan
lives in [docs/phase-5-baseline-implementation.md](phase-5-baseline-implementation.md);
this file records what was actually built and why.

## D-501. Pipeline shape

Implemented `RAGFactChecker` exactly as specified in ADR-0001:
**decompose → per-question retrieve → answer → aggregate → abstain**.

The orchestrator lives in [src/misinfo/pipeline/orchestrator.py](../src/misinfo/pipeline/orchestrator.py).
It wires module-level Protocols (`Decomposer`, `Retriever`, `Answerer`, `Aggregator`,
`AbstentionHead`) so any stage is swappable without orchestrator changes.

## D-502. Inference backend

Pluggable per ADR-0002. `get_backend()` resolves Groq, llama_cpp (stub), or Mock.
The factory wraps the inner backend in `CachingBackend` by default; pass `cache=False`
to opt out (e.g., for `info` CLI inspection).

## D-503. Response cache

Added a sha256-keyed file cache in [src/misinfo/inference/cache.py](../src/misinfo/inference/cache.py).
Key inputs: `(model_id, kind, schema_hash, prompt, max_tokens, temperature, seed)`.
Storage: `<data_dir>/cache/<sanitised_model_id>/<key>.json`, gitignored.

Why: Phase 7 will re-run ablations many times; without a cache every rerun re-burns
Groq quota and breaks reproducibility when network blips. The cache makes reruns
deterministic and offline-safe.

## D-504. Retrieval

BM25 (inline implementation, no `rank-bm25` dep needed at test time) + a lazy-imported
BGE-small dense retriever, fused with Reciprocal Rank Fusion (k=60). Dense retrieval
isn't exercised in unit tests (sentence-transformers is heavy); a stub-based test in
`test_retrieve_hybrid.py` validates the RRF logic.

## D-505. Encoder baseline

Zero-shot DeBERTa-v3-large-MNLI via `transformers.pipeline("zero-shot-classification")`,
no fine-tuning. Three candidate labels (`supports`/`refutes`/`is unrelated to`) map
to verdict labels. Lazy-imports `transformers` so the base install stays slim.

## D-506. Abstention head (Phase 5 stub)

`IdentityAbstentionHead` passes the aggregator's verdict + confidence through
unchanged. Real heads (logistic + isotonic, conformal) land in Phase 6 per ADR-0007.
The orchestrator already computes retrieval-quality signals (`mean_top1`,
`evidence_coverage`) so Phase 6 can plug in without orchestrator changes.

## D-507. Eval harness

Pure-NumPy metrics: F1-macro, accuracy, ECE, MCE, AURC, accuracy@coverage, AVeriTeC
recall proxy, abstention rate. Slice support via row-index dicts. Markdown report
writer + JSON dump for downstream notebooks.

The "AVeriTeC recall proxy" is **not** the official Ev2R metric — that needs
reference QA pairs we don't have. Documented in code and in NFR-Repro-1.

## D-508. CLI surface

`misinfo {info,verify,batch,eval}` — one subcommand per workflow we'll exercise in
later phases. `info` is offline (`cache=False`) so it doesn't write a cache entry
just to print model metadata.

## D-509. Test gating

Added a `live` pytest marker (default-deselected) for tests that hit Groq. CI runs
`pytest` and stays offline; a developer with `GROQ_API_KEY` set can run
`pytest -m live` for a smoke check.

## Coverage at Phase 5 close

`pytest --cov=src/misinfo` → **73%** total. Headroom modules: `groq_backend` (live
path, gated), `dense.py` (sentence-transformers, lazy), `slices.py` and
`logging.py` (small, exercised in later phases).

## Out of scope (deferred)

- Real abstention heads → Phase 6.
- AVeriTeC v2 ingestion + Ev2R scoring → Phase 7.
- FastAPI service wrapping `RAGFactChecker.verify` → Phase 8.
- Reranker → Phase 6 if recall is the bottleneck.
