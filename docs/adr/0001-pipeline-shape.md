# ADR-0001 — Pipeline shape: decomposition → per-question retrieval → verifier

**Status:** Accepted
**Date:** 2026-05-01

## Context

Phase 1 [DECISION.md](../phase-1/DECISION.md) chose to compete on the AVeriTeC v2 evaluation. The 2025 AVeriTeC-2 shared-task winners (P07 CTU AIC, P08 HerO 2) all use the same shape: claim decomposition into yes/no sub-questions, per-question evidence retrieval, per-question answer extraction, and final verdict aggregation. Phase 1 also wants to expose retrieval-failure as a measurable signal for the abstention head — that requires the per-question structure.

## Decision

```
claim
  → Decomposer        — LLM produces 3 sub-questions
  → Retriever × 3     — hybrid BM25 + dense, top-5 evidence per question
  → Answerer × 3      — per-question answer + citations
  → Aggregator        — pre-abstention {verdict, confidence, rationale, evidence}
  → AbstentionHead    — confidence fusion → maybe override to "Abstain"
```

Each stage is a Protocol in `src/misinfo/pipeline/interfaces.py`; the orchestrator composes them.

## Consequences

- Modules are independently testable and swappable.
- Per-question retrieval gives the abstention head a clean retrieval-quality signal (Phase 1 angle 2 lives inside this).
- Three LLM round-trips per claim — fits the latency budget on Groq (Phase 4 latency table) but not on local 7B Q4 (where it hits the p95 boundary).
- We commit to AVeriTeC's question-decomposition idiom; switching benchmarks later is moderate work.

## Alternatives considered

- **Single-pass RAG (one LLM call with all evidence stuffed in).** Faster but loses leaderboard comparability and per-question observability. Kept as a Phase 5 ablation only.
- **Encoder-only NLI head (DeBERTa-v3).** Cheap and fast but not SOTA on AVeriTeC and no rationale. Kept as Phase 5 baseline reference, not the system.
- **Agentic ReAct fact-checker.** Higher recall on multi-hop claims but eval is harder, latency unstable. Out of scope for the eight-week window.
