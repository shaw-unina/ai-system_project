# ADR-0004 — Retrieval: hybrid BM25 + BGE-small with RRF

**Status:** Accepted
**Date:** 2026-05-01

## Context

The Phase 1 literature shows retrieval is the dominant failure mode in RAG fact-checkers (P07, P20, P24). On AVeriTeC v2's evidence corpus, sparse-only retrievers miss paraphrased evidence; dense-only retrievers miss exact-match cues (numbers, named entities). Hybrid retrieval consistently outperforms either alone (14-18 pt gain in some studies). We have CPU only.

## Decision

- **Sparse:** `rank_bm25` (pure Python). No Lucene / Java dependency.
- **Dense:** `BAAI/bge-small-en-v1.5` (33 M params) via `sentence-transformers`. CPU at ~50-100 ms/query.
- **Fusion:** Reciprocal Rank Fusion (RRF), `1/(k + rank)` with k=60. Top-50 from each → fuse → top-5 to LLM.
- **Index:** FAISS (CPU, file-backed, local). No vector-DB daemon.
- **Reranker:** none in Phase 5. BGE-reranker-v2-m3 reserved for Phase 6 if recall is the bottleneck.

## Consequences

- All-CPU retrieval. Cheap, reproducible, file-based.
- One additional Python dep (`sentence-transformers`) and FAISS — added in a Phase 5 optional-deps group.
- Retrieval is the same regardless of inference backend — keeps Groq vs llama_cpp comparable.

## Alternatives considered

- **BM25 only.** Simpler. Underperforms on paraphrased evidence (Phase 1 P24). Kept as an ablation.
- **Dense only (E5 / BGE-base).** Misses exact cues. Kept as an ablation.
- **ColBERTv2.** Strong but heavier engineering and slower on CPU. Reconsider in Phase 6 if needed.
- **Pyserini / Lucene.** Heavier, JVM dependency.
- **Chroma / Qdrant / LanceDB.** Require a service or dataset format we don't need at this scale.
