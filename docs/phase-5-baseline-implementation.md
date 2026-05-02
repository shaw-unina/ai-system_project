# Phase 5 — Baseline Implementation (Innovation): Plan

## Context

Phase 4 froze the contracts and module boundaries: `Verdict` schema, `LanguageModel` Protocol with `GroqBackend` primary, `FactChecker` + per-stage Protocols (`Decomposer`, `Retriever`, `Answerer`, `Aggregator`, `AbstentionHead`), Langfuse Cloud tracing wired in.

Phase 5 turns the contracts into running code: the full **decomposition → retrieval → answer × N → aggregate → abstain → Verdict** pipeline, two reference baselines for ablation, an evaluation harness that measures the Phase 2 NFR metrics end-to-end, a CLI, and a Groq response cache so reruns are offline.

This is the biggest single phase. The output of Phase 5 is the **innovation half of the project running end-to-end on a public AVeriTeC v2 dev sample**, with metrics that the Phase 6 (proposed method) and Phase 7 (controlled experiment) work both build on. The proposed-method work — the abstention head — is **deferred to Phase 6** by design (per ADR-0007). Phase 5 ships a passthrough stub so the orchestrator runs end-to-end.

## Goals

1. The pipeline produces a `Verdict` for any English claim end-to-end via Groq.
2. Two reference baselines exist alongside the system: **single-pass RAG** and **zero-shot NLI encoder** (no fine-tuning — see scope rationale below).
3. The **evaluation harness** computes F1 / macro-F1 / ECE / AURC / accuracy@coverage / AVeriTeC-score + per-topic and per-attack-style slices.
4. A **CLI** (`misinfo …`) exposes verify / batch / eval / data subcommands.
5. A **file-based response cache** keyed on `(model_id, prompt_hash, seed, temperature)` makes reruns offline and deterministic at the call level.
6. Tests cover every module with `MockBackend`; live Groq runs are gated behind a `--run-groq` marker.
7. Phase 2 NFRs verifiable in this phase pass: NFR-Acc-1 baseline metric, NFR-Expl-1 (every verdict carries evidence + rationale), NFR-Repro-1/2 (cache + seed control), NFR-Maint-1 coverage trajectory.

## Scope rationale (read this first)

**No real fine-tuning of the encoder baseline.** Fine-tuning DeBERTa-v3 on AVeriTeC requires labelled training data, GPU time, and a hyperparameter sweep. None of these are available cleanly on CPU/Apple Silicon, and the encoder is *only* a reference in our framing (Phase 1 §6 explicitly demoted it). The encoder baseline therefore uses **zero-shot NLI** with `MoritzLaurer/DeBERTa-v3-large-mnli-fever-anli-ling-wanli` (already trained on FEVER+ANLI; CPU-runnable). If accuracy comes out absurdly low we can revisit.

**Decomposer / Answerer / Aggregator are LLM stages on Groq.** The retrieval stack (BM25 + BGE-small + RRF) is CPU-local.

**AVeriTeC corpus.** Phase 5 implements the loader and small-sample workflow. Full corpus indexing is a separate user-triggered command (`misinfo data download averitec --full`) — not run in CI.

**Abstention head.** Phase 5 ships `IdentityAbstentionHead` (passthrough — Verdict.confidence = AggregatorOutput.confidence; never overrides to Abstain). Real heads land in Phase 6 (per ADR-0007).

## Approach

### 1. Concrete pipeline stages (`src/misinfo/{decompose,retrieve,verify,abstention,pipeline}/`)

| Module | Class | Backed by |
|---|---|---|
| `decompose/llm_decomposer.py` | `LLMDecomposer` | `LanguageModel.generate_structured(... SubQuestionList)` |
| `retrieve/bm25.py` | `BM25Retriever` | `rank_bm25` over a tokenized corpus |
| `retrieve/dense.py` | `DenseRetriever` | `sentence-transformers` BGE-small + FAISS-CPU |
| `retrieve/hybrid.py` | `HybridRetriever(BM25Retriever, DenseRetriever, k=60)` | RRF fusion |
| `retrieve/corpus.py` | `EvidenceCorpus`, `build_index()` | Loads AVeriTeC evidence pages, builds BM25 + FAISS |
| `verify/answerer.py` | `LLMAnswerer` | LLM call per (question, evidence) → `QuestionAnswer` |
| `verify/aggregator.py` | `LLMAggregator` | LLM call → `AggregatorOutput` |
| `abstention/identity.py` | `IdentityAbstentionHead` | passthrough |
| `pipeline/orchestrator.py` | `RAGFactChecker(FactChecker)` | composes the above; emits `Verdict` |

Each LLM stage:
- Loads its prompt from `src/misinfo/pipeline/prompts/{stage}.txt` (versioned).
- Hashes the prompt template + variables for the cache key.
- Wraps the call in `@traced(...)`.

**Note on parallelism.** The three Answerer calls per claim are independent. Phase 5 runs them sequentially for simplicity; Phase 8 may add `asyncio.gather` if NFR-Lat-1 is breached under load.

### 2. Reference baselines (`src/misinfo/baselines/`)

- `baselines/single_pass.py` → `SinglePassRAGFactChecker` — implements the same `FactChecker` Protocol but does ONE LLM call with all evidence stuffed into the prompt. No decomposition, no per-question retrieval. Phase 7 ablation.
- `baselines/encoder.py` → `EncoderBaseline` — zero-shot NLI head over `[claim] [SEP] [evidence]` using DeBERTa-v3-large-MNLI. Outputs `Verdict` with the NLI softmax as confidence. CPU-only via `transformers`.

Both produce the same `Verdict` schema as the main system, so the eval harness scores them identically.

### 3. Evaluation harness (`src/misinfo/eval/`)

```
src/misinfo/eval/
├── __init__.py
├── metrics.py      # f1_macro, ece, mce, aurc, acc_at_coverage, averitec_score (Ev2R-style proxy)
├── slices.py       # build per-topic and per-attack-style index over a dataset
├── harness.py      # run_eval(factchecker, dataset, slices) → Results
├── reports.py      # write Markdown report + push Langfuse dataset (when enabled)
└── results.py      # Pydantic Results object (per-claim records + aggregate + slices)
```

Key contracts:

```python
def run_eval(
    factchecker: FactChecker,
    dataset: list[ClaimRecord],
    slices: dict[str, list[int]] | None = None,
    seed: int = 42,
) -> Results: ...
```

`Results` records the full `Verdict` per claim, plus aggregate metrics, plus per-slice metrics. Saved to `reports/eval/<system>/<dataset_hash>/<run_id>.json`.

Metrics implemented in pure NumPy / scipy with no PyTorch dependency. ECE uses 10 equal-mass bins. AURC integrates the risk–coverage curve. AVeriTeC-score is a recall-style proxy (we cannot exactly reproduce the official Ev2R metric without the leaderboard's reference QA pairs; we document this explicitly in the report).

### 4. Response cache (`src/misinfo/inference/cache.py`)

```
class CachingBackend(LanguageModel):
    """Wraps any LanguageModel; reads from / writes to data/cache/groq/."""
```

- Cache key: `sha256(model_id || prompt || max_tokens || temperature || seed || schema_hash)`.
- Cache value: JSON `{response: str, model_version: str, generated_at: str}`.
- Default ON when `MISINFO_CACHE=1` (we'll set it in `.env` for dev).
- File-based; one file per key; `data/cache/groq/` is gitignored (already covered).

Phase 4's risk-#3 mitigation lands here: a flaky network during eval cannot break a rerun.

### 5. CLI (`src/misinfo/cli.py`)

Use `argparse` (no new dep — Typer was deferred). Subcommands:

```
misinfo verify "<claim>"                                  # FR-1, UC-1
misinfo batch <input.csv> <output.csv>                    # FR-4, UC-2
misinfo data download averitec --version v2 --split dev   # writes data/raw/averitec/...
misinfo data attack-set --styles newswire,tabloid,social  # FR-7, UC-3
misinfo data verify                                       # check manifest hashes
misinfo eval --system rag|single-pass|encoder \
             --split dev|attack-newswire|attack-tabloid|...
misinfo info                                              # backend, settings, git sha
```

Console-script entry point in `pyproject.toml`: `misinfo = misinfo.cli:main`.

### 6. Prompts (versioned, hashed into cache key)

```
src/misinfo/pipeline/prompts/
├── decompose.txt     # claim → sub-questions
├── answer.txt        # (question, evidence) → answer + citation
└── aggregate.txt     # (claim, [Q,A]) → verdict + rationale + confidence
```

Each prompt has a header comment with `# version: N` so changes invalidate the cache.

### 7. Tests (`tests/`)

```
tests/
├── test_metrics.py              # synthetic predictions; check F1/ECE/AURC against analytic values
├── test_pipeline.py             # orchestrator end-to-end with MockBackend
├── test_decomposer.py           # uses MockBackend with a response_factory
├── test_retrieve_bm25.py        # tiny in-memory corpus
├── test_retrieve_hybrid.py      # RRF fusion correctness
├── test_aggregator.py
├── test_cache.py                # cache hit/miss, key stability
├── test_cli.py                  # argparse routing; mock backends
├── test_eval_harness.py         # tiny synthetic dataset → Results
└── test_groq_live.py            # @pytest.mark.live; skipped without GROQ_API_KEY
```

Coverage target: ≥ 60% on `src/misinfo/` (NFR-Maint-1). Use `pytest -m 'not live'` in CI.

### 8. Documentation

- `docs/phase-5-decisions.md` — short ADR-style note, like prior phases.
- README quickstart appended with `misinfo verify "..."` example and a note on the cache.
- Each baseline gets a one-paragraph block in `docs/phase-5-decisions.md` explaining what it is and what it isn't.

## Files to create / modify

```
NEW
src/misinfo/cli.py
src/misinfo/inference/cache.py
src/misinfo/pipeline/orchestrator.py
src/misinfo/pipeline/prompts/{decompose,answer,aggregate}.txt
src/misinfo/decompose/llm_decomposer.py
src/misinfo/retrieve/{bm25,dense,hybrid,corpus}.py
src/misinfo/verify/{answerer,aggregator}.py
src/misinfo/abstention/identity.py
src/misinfo/baselines/__init__.py
src/misinfo/baselines/{single_pass,encoder}.py
src/misinfo/eval/{__init__,metrics,slices,harness,reports,results}.py
tests/test_metrics.py
tests/test_pipeline.py
tests/test_decomposer.py
tests/test_retrieve_bm25.py
tests/test_retrieve_hybrid.py
tests/test_aggregator.py
tests/test_cache.py
tests/test_cli.py
tests/test_eval_harness.py
tests/test_groq_live.py            # marker-gated
docs/phase-5-decisions.md

MODIFIED
pyproject.toml                      # add [retrieval] extras: rank_bm25, sentence-transformers, faiss-cpu, scikit-learn
                                    # add [encoder] extras: transformers, torch (cpu)
                                    # add console-scripts entry point: misinfo = misinfo.cli:main
src/misinfo/__init__.py             # bump __version__ to 0.5.0
src/misinfo/decompose/__init__.py   # export LLMDecomposer
src/misinfo/retrieve/__init__.py    # export retrievers
src/misinfo/verify/__init__.py      # export Answerer, Aggregator
src/misinfo/abstention/__init__.py  # export IdentityAbstentionHead
.env                                # add MISINFO_CACHE=1
.env.example                        # same
```

## Verification

1. `pytest -q -m 'not live'` — all existing 44 tests + ~30 new tests pass on a clean conda env. Only `MockBackend` and synthetic data; no network.
2. Coverage ≥ 60% on `src/misinfo/` (NFR-Maint-1).
3. `misinfo info` prints backend + git SHA + version.
4. `misinfo verify "The Eiffel Tower is in Paris."` returns a `Verdict` end-to-end via Groq, with a Langfuse trace ID populated. (Live; not part of CI.)
5. `misinfo eval --system rag --split dev --limit 20` runs over 20 AVeriTeC dev claims and produces a Markdown report under `reports/eval/`. (Live; not part of CI.)
6. Cache test: same prompt twice → second call returns from disk, no Groq call recorded in Langfuse for the second.
7. Cross-phase: `Verdict.metadata` carries `langfuse_trace_id` (NFR-Trans-2 traceability), `model_version` (NFR-Repro-1 amended), `dataset_hash` (Phase 3 manifest tie-in).

## Risks

1. **Groq rate / cost during eval.** A 200-claim dev run is ~800 LLM calls (1 decompose + 3 answer + 1 aggregate ≈ 5 per claim, with three baselines). Mitigation: cache; `--limit` flag default = 50; document `--full` as a deliberate paid run.
2. **AVeriTeC v2 access.** Some evidence URLs may be dead. Mitigation: prefer the bundled-evidence collection that the v2 task page provides; loader handles missing URLs gracefully.
3. **DeBERTa-v3 model download (~440 MB).** Mitigation: encoder baseline is opt-in via `--system encoder`; download is one-time and cached by HuggingFace.
4. **Sentence-transformers + FAISS install footprint** on Linux CI is ~700 MB. Mitigation: gate the retrieval extras under `[retrieval]` so the base install is small; CI installs the full set.
5. **Eval-harness metric drift** vs official AVeriTeC score. Mitigation: clearly document our score as a *recall-style proxy* and submit to the official leaderboard separately if a member runs the local llama_cpp path.

## Out of scope (deferred)

- The real `AbstentionHead` implementations (temperature scaling, retrieval-gated, fusion) — Phase 6.
- Fine-tuning the encoder baseline.
- Adversarial-paraphrase attack-set generation against a real verifier model — Phase 6 wires the Phase 3 attack pipeline to a real paraphraser; Phase 5 ships only the structured generator code path.
- FastAPI / Docker hardening — Phase 8.
- Frontend dashboard — Phase 10.

## Ordering for execution

If we run Phase 5 in a single sweep, the dependency order is:

1. Cache + CLI scaffold (foundation).
2. Eval metrics + harness + slices (so we can measure as soon as anything runs).
3. Retrieval (BM25 → dense → hybrid → corpus loader).
4. LLM stages (decomposer → answerer → aggregator) backed by `MockBackend` first.
5. Orchestrator wiring all of the above.
6. Encoder baseline + single-pass baseline.
7. Tests fill in alongside each step.
8. Documentation.
