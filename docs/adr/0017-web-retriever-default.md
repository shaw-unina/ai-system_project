# ADR-0017 — Web retriever as default; BM25 retained

**Status:** accepted (Phase 11.1).

## Context

Phase 10 / 11 shipped a closed-book RAG pipeline backed by BM25 over a
fixed corpus. In practice that meant every demo claim outside the corpus
returned `NotEnoughEvidence` with confidence 0 — the system felt broken
even though abstention was technically correct.

## Decision

`MISINFO_RETRIEVER` selects the retriever:

- `web` (default): live Tavily search via
  [src/misinfo/retrieve/web.py](../../src/misinfo/retrieve/web.py). One
  search per sub-question; in-process LRU cache deduplicates within a
  request. On Tavily failure → empty evidence → orchestrator abstains.
- `bm25`: BM25 over the corpus selected by `MISINFO_CORPUS_PATH` /
  `MISINFO_CORPUS_PROFILE`. The Phase 6 calibration was fit on AVeriTeC
  retrieval distributions, so this path is the only one where the
  calibration NFRs (Cal-1/2/3) hold.

If `MISINFO_RETRIEVER=web` but `SEARCH_API_KEY` is empty, the service
logs a warning and falls back to BM25 over the configured corpus
(degrade rather than fail to start).

## Alternatives considered

| Option | Why not |
|---|---|
| Keep BM25-only, ship more corpora | Doesn't actually generalize — every shipped corpus has gaps. Pushes the failure mode around without removing it. |
| Remove BM25 entirely | Calibrated metrics in MODEL-CARD become unreproducible; reviewers can't verify Phase 7 numbers. |
| DuckDuckGo / Serper instead of Tavily | DuckDuckGo HTML scraping is TOS-grey. Serper returns snippets only — we'd need a follow-up fetch. Tavily extracts the relevant span per result, which matches the BM25 contract. |
| Live web + dense rerank | Worth doing, but it's a Phase 12 enhancement, not a v1.0 hardening change. |

## Consequences

- **Calibration NFRs (Cal-1/2/3) apply only on `bm25:averitec`.** The
  model card and `LIMITATIONS.md` say so explicitly.
- **NFR-Repro-1** is amended: bit-identical metrics only on `bm25` +
  `llama_cpp`. The `web` retriever documents per-claim non-determinism.
- **Per-request cost** (Tavily ~$0.005). Bounded by the existing per-key
  rate limit and the 24h cache.
- **Privacy** disclosure expanded: claim text now leaves the box to two
  third parties (LLM + search provider) when `MISINFO_RETRIEVER=web`.
  Documented in `LIMITATIONS.md`.
- **No code path that 5xx's on retriever failure.** Empty evidence →
  abstain is the worst case.
