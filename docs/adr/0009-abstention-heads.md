# ADR-0009 — Concrete abstention heads (Phase 6)

**Status:** Accepted
**Date:** 2026-05-02
**Reads:** [0007-abstention-interface.md](0007-abstention-interface.md)

## Context

ADR-0007 locked the abstention-head interface but explicitly deferred the
concrete head choice to Phase 6. We now need a head set that:

1. Lets Phase 7 ablate the **value of retrieval-quality signals** (the
   distinctive Phase 1 angle-2 finding) vs. verifier-only calibration.
2. Covers parametric and non-parametric calibration so we can tell whether the
   miscalibration shape is sigmoid-like or arbitrary.
3. Stays small enough to run all heads in a Phase 7 grid without combinatorial blow-up.

## Decision

Ship four concrete heads + the Identity control:

- **`IdentityAbstentionHead`** (Phase 5, retained) — control variable. Tests
  whether *any* abstention helps over the raw verifier.
- **`TemperatureScalingHead`** — cheapest parametric calibrator. Fits a single
  scalar `T` over verifier confidence in log-odds space (Guo et al. 2017,
  reduced to scalar). Gives a clean answer to: "is the verifier just
  over-confident?"
- **`IsotonicCalibrationHead`** — non-parametric monotonic mapping
  (sklearn `IsotonicRegression`). Robust to arbitrary miscalibration shape;
  costs more calibration data.
- **`RetrievalGatedHead`** — hard rule that overrides verifier confidence to 0
  whenever `evidence_coverage` or `mean_top1` falls below grid-fit thresholds.
  Tests the *necessity* of the retrieval signal as a gate, isolated from any
  learned interaction.
- **`LogisticFusionHead`** — `LogisticRegression` over `[verifier_conf,
  mean_top1, evidence_coverage]`. The headline research contribution: tests
  whether *learned* fusion of verifier + retrieval signals beats either alone.

A split-conformal head was considered and **deferred**: conformal would give
distribution-free coverage guarantees but adds another calibration fold, and
the H1 hypotheses don't require coverage guarantees — only F1 retention at a
target coverage.

## Consequences

- Phase 7 runs five system variants × clean + 3 attack families × τ sweep. The
  grid is small enough to fit in a single notebook.
- The `Fusion` head is the only one that uses all three input signals — a
  failure mode of `Fusion` while `RetrievalGated` succeeds would tell us the
  signal–verifier interaction is non-monotone, which is itself a research
  finding.
- Adding the conformal head later is one new file; nothing in the orchestrator
  or registry would change.

## Alternatives considered

- **Bayesian calibration head.** Rejected: marginal gain over isotonic on the
  data scale we have; large engineering cost.
- **Per-class temperature scaling.** Rejected for now: verifier output is a
  single confidence in [0, 1], not a logit vector. Revisit if H1.c fails.
- **Reranker as the abstention signal.** Rejected: conflates two
  ablation knobs (retriever quality and abstention) and would force a Phase 6
  rewrite of the retrieval module.
