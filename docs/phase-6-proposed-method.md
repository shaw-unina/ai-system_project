# Phase 6 — Proposed Method: Calibrated Selective Prediction

**Status:** Implemented
**Reads:** [phase-1/DECISION.md](phase-1/DECISION.md), [phase-2/HYPOTHESES.md](phase-2/HYPOTHESES.md), [adr/0007-abstention-interface.md](adr/0007-abstention-interface.md)
**Read by:** Phase 7 (controlled comparison + statistical tests)

## What Phase 6 ships

The research contribution: a pluggable family of *calibrated abstention heads*
plus an orchestrator-level τ override. With these in place, Phase 7 can swap
the head as a single ablation variable and run the H1.a–d statistical battery.

```
RAGFactChecker(
  decomposer, retriever, answerer, aggregator,
  abstention=<one of: identity, temperature, isotonic, retrieval_gated, fusion>,
  abstain_threshold=<τ>,
)
```

When `abstention.score(...)` returns confidence `< τ`, the orchestrator
overrides the verdict to `"Abstain"`. τ is selected on a held-out fold to hit a
target coverage (default 0.7, per H1.b).

## Heads

| Head | Inputs | Fitting |
|---|---|---|
| `IdentityAbstentionHead` | verifier conf | none — Phase 7 control |
| `TemperatureScalingHead` | verifier conf | scalar `T` via NLL minimisation in log-odds space |
| `IsotonicCalibrationHead` | verifier conf | `IsotonicRegression` (sklearn) |
| `RetrievalGatedHead` | retrieval signals + verifier conf | 2-D grid search over `(coverage_min, top1_min)` |
| `LogisticFusionHead` | verifier conf + `mean_top1` + `evidence_coverage` | `LogisticRegression` on 3 features |

All heads implement `fit(records)`, `save(path)`, `load(path)`, and `score(agg,
signals)`. JSON persistence for the parametric/numeric heads; joblib for the
sklearn-backed ones.

## Calibration record

`src/misinfo/abstention/base.CalibrationRecord`:

```python
@dataclass(frozen=True)
class CalibrationRecord:
    verifier_confidence: float
    mean_top1: float
    evidence_coverage: float
    correct: bool
```

JSONL format (one record per line) is the calibrate CLI input. The eval
harness writes this format from `Results.per_claim` (each `ClaimResult` now
carries a `signals` dict).

## Threshold selection

`select_threshold_for_coverage(confidences, target_coverage) → τ` returns the
`(1 − target_coverage)`-quantile so that a fraction equal to `target_coverage`
of inputs are accepted. Phase 7 will run a 3-way fold split (calibration /
threshold / eval) to avoid coverage–accuracy double-dipping.

## CLI surface

```
misinfo calibrate --head <name> --records <jsonl> --output <path>

misinfo eval --input <jsonl> --report <md> \
             --head <name> [--head-path <path>] \
             [--tau <float> | --target-coverage <float>]
```

`info`, `verify`, `batch`, `eval` all share a single head-aware factchecker
builder.

## Tests (offline, MockBackend + synthetic NumPy)

7 new test files, 16 new test cases:

- `test_abstention_temperature.py` — NLL non-increasing after fit; save/load.
- `test_abstention_isotonic.py` — monotonicity of fitted mapping; passthrough on unfit.
- `test_abstention_retrieval_gated.py` — coverage gate forces 0 confidence.
- `test_abstention_fusion.py` — learns retrieval-driven correctness when verifier conf is noise.
- `test_threshold_selection.py` — top-half quantile; full coverage edge case.
- `test_orchestrator_abstain.py` — τ override end-to-end.
- `test_cli_calibrate.py` — `misinfo calibrate` round-trips Temperature + Fusion artefacts.

`pytest` → **79 passed, 1 deselected** (live).

## Open from Phase 6 → Phase 7

- Score every head on AVeriTeC v2 dev clean and on all three attack families.
- Run paired bootstrap (n=10,000) for H1.a, H1.b, H1.c with fixed seeds.
- Verify H1.d (abstention rate ∈ [0.10, 0.50]) per family.
- Pick the headline configuration; record τ + head + dev-set hash.

## Out of scope (deferred)

- Conformal-prediction head — stretch only.
- Per-class calibration — revisit if H1.c fails.
- Online recalibration / drift adaptation — Phase 9.
