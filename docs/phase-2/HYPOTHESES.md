# Research Hypotheses

**Status:** DRAFT
**Reads:** [../phase-1/DECISION.md](../phase-1/DECISION.md), [REQUIREMENTS.md](REQUIREMENTS.md)
**Read by:** Phases 6, 7

This file operationalises the Phase 1 hypothesis. Numerical thresholds match [DECISION.md §3](../phase-1/DECISION.md). When the eventual research report quotes a number, it traces to a row here.

## H1 — Primary hypothesis (verbatim from Phase 1)

> A RAG fact-checker calibrated with insufficient-evidence abstention preserves ≥ 80% of its in-distribution accuracy at coverage ≥ 0.7 when evaluated against three families of LLM-generated paraphrase attacks, whereas the same system without abstention loses ≥ 15 absolute F1 points on at least one attack family.

H1 is the disjunction of an attack-vulnerability claim and an abstention-recovery claim. We split it into four sub-hypotheses to make the test concrete.

## Sub-hypotheses

### H1.a — Vulnerability of the no-abstention baseline

| Field | Value |
|---|---|
| Claim | Without abstention, the baseline RAG fact-checker loses ≥ 15 abs F1 points on at least one attack family vs the clean AVeriTeC v2 dev distribution. |
| Metric | Macro-F1 (verdict) |
| Datasets | AVeriTeC v2 dev (clean) vs LLM-paraphrase attack set (newswire / tabloid / social) |
| Statistical test | Paired bootstrap, n = 10 000 resamples; one-sided test on F1 difference |
| Reject if | Max F1 drop across all three attack families < 15 abs pts at p ≤ 0.05 |
| Report figure | Table 1, Figure 2 of final report |
| Traces to | NFR-Acc-2, NFR-Rob-1 |

### H1.b — Abstention recovery

| Field | Value |
|---|---|
| Claim | With abstention enabled, F1 retention ≥ 80% of clean-distribution F1 across all three attack families at coverage ≥ 0.7. |
| Metric | F1 at coverage 0.7, normalised to clean-distribution F1 |
| Datasets | Same as H1.a |
| Statistical test | Per-family one-sided paired bootstrap; require all three to pass at p ≤ 0.05 |
| Reject if | Any one of the three families fails the threshold |
| Report figure | Table 2, Figure 3 (risk–coverage curves) of final report |
| Traces to | NFR-Acc-2, NFR-Cal-2 |

### H1.c — Calibration improvement

| Field | Value |
|---|---|
| Claim | Under attack, the abstention-enabled system has ECE ≤ ECE of the no-abstention system. |
| Metric | ECE with 10 confidence bins; report Abstain-ECE per P32 (SelectLLM) for the abstention-enabled system. |
| Datasets | Per-family attack sets |
| Statistical test | Bootstrap CI on ECE difference; non-overlapping CIs at 95% counts as supported |
| Reject if | ECE difference is statistically indistinguishable from zero or negative |
| Report figure | Reliability diagrams, Figure 4 |
| Traces to | NFR-Cal-1 |

### H1.d — Null guard (anti-trivial-abstention)

| Field | Value |
|---|---|
| Claim | The abstention rate per attack family stays in [0.10, 0.50]. |
| Why | Without this, H1.b can be satisfied by simply abstaining on every attacked claim, which would be useless in deployment. |
| Metric | Fraction of inputs receiving `verdict = Abstain` per family |
| Datasets | Per-family attack sets |
| Reject if | Any family's abstention rate falls outside the band |
| Report figure | Bar chart of abstention rates, Figure 5 |
| Traces to | UC-1, NFR-Acc-2 |

## How H1 is decided

H1 is **supported** iff all four sub-hypotheses pass their reject conditions. If any one fails, the report says so explicitly and the threats-to-validity section explains why. The course rubric rewards a clean rejection more than a hedged "supported with caveats."

## Reproducibility contract for hypothesis tests

- Every reported metric is computed by the harness in `src/misinfo/eval/` (created Phase 5).
- Bootstrap seeds are fixed (`misinfo.repro.seed_everything`).
- The attack set is hashed (`misinfo.repro.hash_dir`) and the hash is recorded in every results CSV.
- Re-running the H1 test from a clean checkout produces bit-identical numbers — this is NFR-Repro-1.
