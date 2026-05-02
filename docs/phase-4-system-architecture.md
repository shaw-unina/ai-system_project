# Phase 4 — System Architecture: Plan

> **REVISED 2026-05-01.** The originally-proposed *local llama.cpp on Apple Silicon* path has been superseded by a **pluggable backend (Groq primary, llama.cpp deferred)** plus **self-hosted Langfuse** for traceability. See [docs/adr/0002-inference-runtime.md](adr/0002-inference-runtime.md) and [docs/adr/0008-observability-langfuse.md](adr/0008-observability-langfuse.md). The pipeline shape and module boundaries are unchanged. Earlier latency-budget figures based on local 7B Q4 are preserved in the appendix as a reference.

## Context

Phase 1 chose the angle (LLM-paraphrase robustness + calibrated abstention). Phase 2 locked the contract: structured `Verdict` output, p50 ≤ 30 s / p95 ≤ 60 s, hardware ≤ 24 GB GPU equivalent. Phase 3 shipped the data layer.

Phase 4 picks the **architecture** the team will actually build. The user has fixed two architectural constraints:

- **Compute target:** CPU / Apple Silicon only (no discrete GPU).
- **Benchmark posture:** target the AVeriTeC-2 leaderboard. The system must adopt the shared-task pipeline shape (claim decomposition → evidence retrieval → structured verifier) so submissions are comparable.

These two together are the dominant constraint pair. They rule out vLLM (no Apple-Silicon support), rule in `llama.cpp` with Metal acceleration, and push us toward a 7-8 B class verifier in 4-bit GGUF rather than 13-70 B options.

This document compares architecture options, picks one with rationale, defines module boundaries, picks concrete tech, and lists the ADRs to land. **No code changes** until the plan is acknowledged.

## Architecture options compared

### Option A — Fine-tuned encoder baseline (DeBERTa-v3 NLI head)

**Shape.** Concatenate `[claim] [SEP] [evidence_concat]` → DeBERTa-v3-large MNLI head → softmax over 4 verdict classes.

**Pros.** Cheap, fast, deterministic, trains to convergence in hours. Strong calibration profile out of the box. Runs on CPU at < 1 s/claim.

**Cons.** Not leaderboard-comparable (AVeriTeC-2 is a generative-evidence task). No native rationale generation. Can't produce evidence-grounded explanations. The Phase 1 literature is unambiguous: encoder-only systems are no longer SOTA on AVeriTeC.

**Verdict.** Keep it as a **baseline-only** in Phase 5 (per [Phase 1 §6: rejected end-to-end zero-shot LLM, kept fine-tuned encoder as baseline reference](phase-1/DECISION.md)). Not the system architecture.

### Option B — Single-pass RAG + LLM verifier

**Shape.** `claim → hybrid retrieve top-k → stuff into one prompt → LLM emits {verdict, rationale}`.

**Pros.** Simple, one round-trip per claim, easy to deploy, easy to reason about. Lowest engineering cost.

**Cons.** Doesn't match AVeriTeC-2's question-decomposition shape. Underperforms on multi-hop / numerical claims. Loses the leaderboard-comparability story.

**Verdict.** Reject as primary; keep as a Phase 5 ablation ("RAG without decomposition").

### Option C — AVeriTeC-2 winning pipeline shape (decomposition → per-question retrieval → verifier) **← chosen**

**Shape.**

```
claim
  └─► Decomposer (LLM) ─► [q1, q2, …, qK]   # yes/no sub-questions
            │
            └─► Retriever (BM25 + BGE-small dense, hybrid)  ─► top-5 evidence per qi
                       │
                       └─► AnswerExtractor (LLM) ─► per-question {answer, citation}
                                  │
                                  └─► Verdict aggregator (LLM, structured output)
                                            ─► {verdict, rationale, evidence_ids}
                                            │
                                            └─► Abstention head ─► confidence ∈ [0,1]
                                                                   maybe override → Abstain
```

This is the shape used by the AVeriTeC-2 winners (CTU AIC, HerO 2 — Phase 1 P07/P08). It hits four needs simultaneously: leaderboard comparability, multi-hop competence, native rationale generation, and clean module boundaries we can swap or ablate.

**Pros.** SOTA-shape. Each module is independently testable. Question decomposition naturally produces an audit trail for the rationale. Retrieval failure (Phase 1 angle 2) is observable per-question — feeds the abstention head cleanly.

**Cons.** Three LLM round-trips per claim (decompose, extract×K, aggregate). On Apple Silicon Q4 7B, that means ~4–8 s decode time × 3 + retrieval ≈ 15–30 s per claim. Within Phase 2's p95 ≤ 60 s budget but **tight**. We mitigate by (a) batching question extraction in a single forward pass when possible and (b) capping K = 3 sub-questions for the controlled experiment. Fallback path documented below.

**Decision.** **Option C.** It is the only architecture that meets the leaderboard-comparability constraint while preserving observability of the Phase 1 failure modes.

## Module boundaries

```
src/misinfo/
├── data/                      # Phase 3 (done)
├── pipeline/                  # NEW — orchestration
│   ├── __init__.py
│   ├── orchestrator.py        # FactChecker.verify(claim) → Verdict
│   └── prompts/               # versioned prompts per stage
├── decompose/                 # NEW — claim → questions
│   ├── __init__.py
│   └── llm_decomposer.py
├── retrieve/                  # NEW — evidence retrieval
│   ├── __init__.py
│   ├── bm25.py                # whoosh / rank_bm25
│   ├── dense.py               # BGE-small via sentence-transformers
│   ├── hybrid.py              # reciprocal-rank fusion
│   └── corpus.py              # AVeriTeC evidence index loader
├── verify/                    # NEW — answer extraction + verdict aggregation
│   ├── __init__.py
│   ├── answerer.py
│   └── aggregator.py
├── abstention/                # NEW — confidence head (Phase 6 fills it)
│   ├── __init__.py
│   └── head.py                # stub interface in Phase 4
├── inference/                 # NEW — model runtime adapter
│   ├── __init__.py
│   ├── base.py                # LanguageModel protocol
│   └── llama_cpp_backend.py   # llama-cpp-python adapter
├── schemas.py                 # NEW — pydantic models for Verdict, EvidenceRef, etc.
└── eval/                      # Phase 5 (later)
```

**Contracts (locked here, implemented later):**

```python
# schemas.py — frozen at Phase 4 close
class EvidenceRef(BaseModel):
    source_id: str
    url: str | None
    span: str
    score: float

class Verdict(BaseModel):
    verdict: Literal["Supported", "Refuted", "NotEnoughEvidence", "Abstain"]
    confidence: float  # ∈ [0, 1]
    evidence: list[EvidenceRef]
    rationale: str
    metadata: dict

# inference/base.py
class LanguageModel(Protocol):
    def generate(self, prompt: str, *, max_tokens: int, temperature: float, seed: int) -> str: ...
    def generate_structured(self, prompt: str, schema: type[BaseModel], *, seed: int) -> BaseModel: ...

# pipeline/orchestrator.py — the only public API surface
class FactChecker:
    def verify(self, claim: str) -> Verdict: ...
    def batch_verify(self, claims: list[str]) -> list[Verdict]: ...
```

This is the contract Phase 5 (baseline) and Phase 8 (FastAPI) wrap. Once locked, downstream phases can build modules in parallel.

## Tech stack — chosen

| Layer | Choice | Why | Alternatives considered |
|---|---|---|---|
| **Inference runtime** | **Pluggable** (`MISINFO_BACKEND`); Groq primary, `llama-cpp-python` optional reference | Hosted Groq solves the Apple-Silicon latency squeeze and unlocks larger models; local path retained for offline / privacy / leaderboard runs. See [ADR-0002](adr/0002-inference-runtime.md). | vLLM (no Apple Silicon); MLX (Apple-only); Ollama (extra daemon) |
| **Verifier model (primary, hosted)** | **`llama-3.3-70b-versatile` on Groq** | Free-tier capable, JSON-mode reliable, multi-hop strong, fast (~500 tok/s) | OpenAI GPT-4-class (closed-weight); Mixtral 8x7B (slower JSON-mode) |
| **Verifier model (fallback, hosted)** | **`qwen/qwen-2.5-32b` on Groq** | Cross-model parity check for Phase 7 ablation | Same as above |
| **Verifier model (local reference)** | **Qwen-2.5-7B-Instruct Q4_K_M GGUF** via `LlamaCppBackend` (deferred) | For NFR-Repro-1 bit-identical runs, offline use, leaderboard submission | Phi-3.5-mini-3.8B |
| **Paraphraser model** (Phase 6 attack set) | Same Qwen-2.5-7B-Instruct, different prompt | One model, two roles — keeps env simple | A second model (rejected to keep complexity down) |
| **Sparse retriever** | `rank_bm25` (pure Python) | Tiny dep, no Java, no Lucene; AVeriTeC corpora are small enough | `whoosh`, `pyserini` (overkill) |
| **Dense retriever** | `BAAI/bge-small-en-v1.5` via `sentence-transformers` | 33 M params, runs on CPU at 50–100 ms/claim, strong on RAG fact-checking | bge-base (heavier), E5-small (similar) |
| **Vector index** | FAISS (CPU, local, file-backed) | No daemon, fits Phase 3 manifest model, already a transitive dep of sentence-transformers via faiss-cpu | Chroma / Qdrant (require running a service) |
| **Hybrid fusion** | Reciprocal-rank fusion (RRF) over BM25 + dense, top-50 → top-5 | Standard, parameter-light; `1/(k+rank)` with k=60 | Linear interpolation on scores (sensitive to score normalisation) |
| **Reranker** | None in Phase 5; BGE-reranker-v2-m3 considered for Phase 6 if recall headroom remains | Avoid the cross-encoder cost upfront | Cohere rerank-3 (closed-source, cost) |
| **Structured output** | Groq JSON-mode (`response_format=json_object`) + pydantic-validate retry; GBNF reserved for the local backend | One contract, zero parse-error rabbit holes; the schema's JSON Schema is auto-injected into the prompt | Outlines / Instructor (extra deps); regex parse (fragile) |
| **Observability** | **Self-hosted Langfuse v2** (2 containers in compose) with `@observe()` on every stage and backend call | Replaces ad-hoc CSVs as the run-of-record; `Verdict.metadata.langfuse_trace_id` gives every output a clickable lineage. See [ADR-0008](adr/0008-observability-langfuse.md). | Langfuse v3 (6 containers, overkill); LangSmith (hosted, paid); print logging |
| **Serving** | FastAPI (already in Phase 8 plan); pipeline mounted as in-process dependency | One container | Triton, Ray Serve (overkill) |
| **Container** | Existing Phase 0 multi-stage Dockerfile, extended to include `llama-cpp-python` with Metal/CPU build flags | Already proven | Distroless (heavier ML base images don't ship distroless) |

### Latency budget breakdown (per claim) — revised

| Stage | Groq Llama-3.3-70B (primary) | Local 7B Q4 (reference, deferred) |
|---|---|---|
| Decompose claim → 3 sub-questions | 0.5–1.0 s | 3–5 s |
| Hybrid retrieval × 3 | 0.3–0.6 s | 0.3–0.6 s |
| Per-question answer extraction × 3 | 1.5–3.0 s | 12–20 s |
| Verdict aggregation | 0.8–1.5 s | 4–8 s |
| Abstention head | < 50 ms | < 50 ms |
| **Total p50** | **~4 s** | ~25 s |
| **Total p95** | **~8 s** | ~50 s |

NFR-Lat-1 (`p50 ≤ 30 s, p95 ≤ 60 s`) is comfortably met under the primary Groq path. Headroom is large enough to allow a Phase 6 reranker if recall is the bottleneck. The local path remains within budget but tight; see appendix for the original analysis.

## ADRs to land in Phase 4

Each ADR is a short markdown file under `docs/adr/`. Format: context → decision → consequences → alternatives.

All ADRs live under [docs/adr/](adr/). Index:

- [ADR-0001](adr/0001-pipeline-shape.md) Pipeline shape: decomposition → per-question retrieval → verifier.
- [ADR-0002](adr/0002-inference-runtime.md) Inference runtime: pluggable; Groq primary, llama-cpp-python optional reference.
- [ADR-0003](adr/0003-verifier-model.md) Verifier model: Llama-3.3-70B via Groq, Qwen-2.5-32B fallback.
- [ADR-0004](adr/0004-retrieval-hybrid.md) Retrieval: hybrid BM25 + BGE-small with RRF, k=5.
- [ADR-0005](adr/0005-structured-output.md) Structured output: JSON-mode + pydantic-validate retry.
- [ADR-0006](adr/0006-output-schema.md) Output schema: `Verdict` from [SCOPE.md](phase-2/SCOPE.md), frozen.
- [ADR-0007](adr/0007-abstention-interface.md) Abstention head: pluggable interface; concrete head specified by Phase 6.
- [ADR-0008](adr/0008-observability-langfuse.md) Observability: Langfuse v2 self-hosted.

## Files to create in Phase 4

```
docs/adr/
├── README.md                  index + ADR template
├── 0001-pipeline-shape.md
├── 0002-inference-runtime.md
├── 0003-verifier-model.md
├── 0004-retrieval-hybrid.md
├── 0005-structured-output.md
├── 0006-output-schema.md
└── 0007-abstention-interface.md

src/misinfo/schemas.py         # frozen pydantic models
src/misinfo/inference/__init__.py
src/misinfo/inference/base.py  # LanguageModel protocol (no impl yet)
src/misinfo/pipeline/__init__.py
src/misinfo/pipeline/interfaces.py  # FactChecker abstract base + module protocols
src/misinfo/decompose/__init__.py   # placeholder + Decomposer protocol
src/misinfo/retrieve/__init__.py    # placeholder + Retriever protocol
src/misinfo/verify/__init__.py      # placeholder + Answerer / Aggregator protocols
src/misinfo/abstention/__init__.py  # placeholder + AbstentionHead protocol

tests/test_schemas.py          # Verdict round-trips JSON; rejects bad enum
tests/test_pipeline_interfaces.py  # protocols match expected method signatures

docs/phase-4-decisions.md      # short ADR-style summary, like phase-3-decisions.md
```

**No model code yet.** Phase 4 lands the protocols and the ADRs; Phase 5 implements them. This split keeps Phase 4 reviewable in one sitting and lets us catch contract issues before any 7B model gets downloaded.

## Verification

1. `pytest -q` — all existing 31 tests pass + the 2 new schema/protocol tests.
2. `python -c "from misinfo.pipeline.interfaces import FactChecker; from misinfo.schemas import Verdict; print(Verdict.model_json_schema())"` — schema matches Phase 2 SCOPE.md verbatim.
3. Each ADR is referenced from this plan and from `phases.md` → Phase 4.
4. Cross-phase trace: every NFR in Phase 2 with verification phase 5/8 has a module that owns it (NFR-Lat-1 → inference + pipeline; NFR-Expl-1 → verify; NFR-Cal-2 → abstention; etc.).

## Out of scope

- Implementing the actual decomposer / retriever / verifier — Phase 5.
- Downloading model weights — Phase 5.
- Wiring FastAPI — Phase 8.
- Choosing reranker / additional retrieval components beyond hybrid — measured in Phase 7, added if recall is the bottleneck.
- Multi-GPU / distributed inference — out (single-machine constraint).

## Risk register specific to this phase

1. **Latency budget breakage.** 7B Q4 on M2/M3 may cross p95 ≤ 60 s under load. Mitigation: Qwen-2.5-3B fallback documented in ADR-003; latency test in Phase 8 fails the build if breached.
2. **GBNF grammar drift.** Constraining JSON via grammars can lose accuracy if too tight. Mitigation: ablation in Phase 5 between grammar-constrained vs free-form + parse.
3. **AVeriTeC corpus mismatch.** The leaderboard's evidence corpus changes between editions; our retriever index must rebuild. Mitigation: data-manifest hash already covers this (Phase 3).
4. **Apple Silicon CI.** GitHub Actions doesn't offer Apple Silicon free runners reliably. Mitigation: Phase 9 CI runs on Linux x86_64 with the same `llama-cpp-python` wheels (CPU build); Apple Silicon path documented for local dev.
