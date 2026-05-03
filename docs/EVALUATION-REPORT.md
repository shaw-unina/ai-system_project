# Evaluation Report

This is the consolidated, external-reader-friendly summary of the system's
evaluation. The full per-experiment artefacts live in
[reports/phase7/](../reports/phase7/) and
[reports/_smoke/](../reports/_smoke/).

## Setup

- **System under test:** `misinfo` v1.0.0 (Phase 11 freeze).
- **Baseline:** Phase 5 fine-tuned encoder (`reports/phase5/baseline.md`).
- **Eval set:** AVeriTeC v2 dev (clean) + three LLM-paraphrase styles
  (newswire, tabloid, social).
- **Backend:** `groq` (default) + `llama_cpp` cross-check.
- **Seeds:** three seeds; mean ± 95% bootstrap CI reported for each metric.

## Headline numbers

| Metric | Baseline | misinfo v1.0.0 | Δ |
|---|---|---|---|
| Macro-F1 (clean) | see baseline | see Phase 7 | ≥ 0 (NFR-Acc-1 satisfied) |
| Macro-F1 drop, paraphrase | — | ≤ 10 abs pts | NFR-Acc-2 satisfied |
| ECE | — | ≤ 0.10 | NFR-Cal-1 satisfied |
| Acc@coverage 0.7 | — | ≥ full + 5 pts | NFR-Cal-2 satisfied |
| AURC | — | reported with 95% CI | NFR-Cal-3 satisfied |

Concrete numbers are tag-bound — pull from
[reports/phase7/results.md](../reports/phase7/) for the released version.

## Robustness

- **LLM paraphrase (3 styles).** Per-style F1 reported in
  `reports/phase7/robustness.md`. Tabloid style is the hardest; abstention
  picks up most of the slack.
- **Retrieval failure.** Share of high-confidence wrong verdicts attributable
  to retrieval misses is reported in
  `reports/phase7/error-decomposition.md`.

## Calibration

- **Reliability diagram** in `reports/phase7/calibration.png`.
- **Risk–coverage curve** in `reports/phase7/risk-coverage.png`. AURC with
  bootstrap CI in the same report.
- Calibration parameters and τ selection: `reports/phase6/`.

## Fairness

- **Topical-slice F1 spread:** ≤ 10 abs points (NFR-Fair-1).
- **Abstention-rate spread:** ≤ 0.20 (NFR-Fair-2).
- Per-slice tables in `reports/phase7/fairness.md`.

## Performance

p50 / p95 latency and throughput measured in
[reports/phase-11/](../reports/phase-11/) at release time. Budgets:

- p50 ≤ 30 s, p95 ≤ 60 s (NFR-Lat-1).
- ≥ 10 claims/min sustained (NFR-Tput).

## Reproducibility

`Verdict.metadata` carries `(backend, model_id, model_version, seed,
temperature, langfuse_trace_id)`. On the optional `llama_cpp` backend,
metrics are bit-identical across re-runs at the same commit + config + data
hash. On the default `groq` backend, results reproduce within the
cross-machine tolerances documented in
[phase-2/SUCCESS-CRITERIA.md](phase-2/SUCCESS-CRITERIA.md).

## Threats to validity

1. **Provider drift.** Groq may change underlying model weights without
   changing the public ID. Captured in `metadata.model_version` when
   available; flagged in the model card.
2. **Test-set contamination.** AVeriTeC v2 dev may overlap with the LLM's
   training data. Mitigation: the `llama_cpp` cross-check uses a fixed
   open-weights model; provider-side contamination cannot move the
   numbers.
3. **Adversarial paraphrase coverage.** Three styles do not exhaust the
   attack surface; results are *indicative*, not exhaustive.
4. **Annotator labels.** AVeriTeC inherits its label noise; we do not
   re-annotate.
