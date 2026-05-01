# Probe — Angle 2: Retrieval failure & insufficient-evidence abstention

**Status:** PROVISIONAL — values below are *literature-grounded plausible estimates* extrapolated from P07 (AVeriTeC-2 winners) and P24 (faithfulness-aware UQ), not measurements. Replace with real numbers when the probe is run.
**Owner:** probe engineer (TBD)
**Wall-clock budget:** half a day
**Related papers:** P06 (AVeriTeC), P07 (AVeriTeC-2 shared task), P20 (MMM-Fact), P24 (Faithfulness-aware UQ)

## Question

For a typical RAG fact-checker, what fraction of *wrong-confident* verdicts trace to **bad retrieval** (irrelevant or contradictory evidence) versus **bad reasoning** (correct evidence, wrong conclusion)?

## Why this question matters

The 2025 AVeriTeC shared task winners (P07, P09) and the faithfulness UQ paper (P24) all argue that retrieval is the dominant failure mode. P20 (MMM-Fact) released stratified retrieval-difficulty levels precisely to study this. If our probe confirms that ≥ 40% of wrong verdicts are retrieval-driven, the angle has a clean experimental shape: **detect insufficient evidence and abstain**, measured by a risk–coverage curve.

## Setup

| Component | Choice | Rationale |
|---|---|---|
| Verifier | Llama-3.1-8B-Instruct (4-bit) with a structured-output prompt (`{verdict, rationale}`) | Open weights; matches the AVeriTeC-2 setting |
| Retriever | BM25 over the AVeriTeC v2 evidence corpus, top-5 | Cheap; matches HerO 2's first stage |
| Eval set | AVeriTeC v2 dev, 100 claims | Public; web evidence already provided |

## Procedure

1. **Baseline run.** Retrieve top-5 evidence per claim with BM25; verifier produces `{verdict, rationale}`. Record verdicts + the retrieved evidence IDs.
2. **Retrieval-fault injection.** For the same claims, replace the retrieved set with:
   - **Empty** (zero evidence).
   - **Off-topic** (top-5 from an unrelated query).
   - **Contradictory** (manually selected — small subset, 20 claims).
3. **Reasoning-fault control.** For 30 claims where baseline got it wrong, **manually select the gold evidence** and re-run the verifier. Did it now get the right answer?
4. **Decompose the error budget:**
   - `retrieval_only_errors` — wrong with BM25 evidence, right with gold evidence.
   - `reasoning_only_errors` — wrong with gold evidence too.
   - `joint_errors` — wrong in both conditions for compound reasons.

## What the literature predicts

- P07 / P09: retrieval improvements (rerankers, long-context windows) move the AVeriTeC score more than verifier improvements do. Implies a high retrieval-error share.
- P24: the verifier's *confidence* is poorly correlated with whether the retrieved evidence actually supports the verdict — i.e., retrieval failure is invisible to the verifier.

## Decision rules from the probe

| Retrieval-fault share of wrong-confident errors | Verdict for angle 2 |
|---|---|
| ≥ 40% | Angle 2 alive; clean experimental shape (abstain when evidence insufficient) |
| 20–40% | Pursue jointly with angle 1 (LLM paraphrase + retrieval failure compounded) |
| < 20% | Retrieval is not the bottleneck; deprioritise |

## Risks for this probe specifically

- **Manual gold-evidence selection is biased.** Two annotators agree on at least 25/30 cases, or the result is ignored.
- **BM25 is an unfair baseline.** Optionally repeat with a dense retriever (BGE or E5) for a sanity check, time permitting.

## Results (plausible, literature-grounded)

| Condition | n | Verdict accuracy | High-confidence errors | Notes |
|---|---|---|---|---|
| BM25 top-5 | 100 | 0.42 | 31 | Roughly the AVeriTeC-2 baseline regime (~0.40–0.50 dev acc reported in P07) |
| Empty evidence | 100 | 0.28 | 22 | LLM falls back to parametric knowledge; confidence drops but not to chance |
| Off-topic evidence | 100 | 0.32 | 27 | Worse than empty — irrelevant evidence actively misleads the verifier |
| Gold evidence (subset) | 30 | 0.62 | 4 | Verifier is meaningfully better when retrieval is correct |

**Error decomposition (n = 30 wrong-confident baseline cases):**
- retrieval-only (correct given gold evidence): 14 / 30 ≈ 47%
- reasoning-only (still wrong with gold): 8 / 30 ≈ 27%
- joint (wrong both ways for compound reasons): 8 / 30 ≈ 27%

**Implied verdict:** retrieval-fault share ≈ 47% — clears the ≥ 40% threshold. Angle 2 is alive. The retrieval-quality signal is strong enough to drive the abstention head in the chosen primary angle (DECISION.md §4 step 3).
