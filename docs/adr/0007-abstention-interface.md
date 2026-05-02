# ADR-0007 — Abstention head: pluggable interface, implementation deferred

**Status:** Accepted
**Date:** 2026-05-01

## Context

Phase 1's primary research angle is calibrated abstention under LLM-paraphrase attack. The exact form of the abstention head (post-hoc temperature scaling, isotonic regression, learned head, signal-fusion rule) is itself a Phase 6 research decision. Phase 4 should not pre-empt that.

## Decision

- The interface is locked: `AbstentionHead.score(aggregator_output, retrieval_signals) → (label, confidence)`.
- Multiple inputs feed `retrieval_signals`: top-k similarity score, evidence-claim NLI alignment, retrieval-error indicator (per Phase 1 angle 2 probe).
- The orchestrator owns the threshold τ override → "Abstain".
- Phase 6 implements concrete heads as separate classes (e.g. `TemperatureScalingHead`, `RetrievalGatedHead`, `FusionHead`); each is a controlled-experiment variable in Phase 7.

## Consequences

- Phase 7 ablations are clean: swap the head, hold the rest of the pipeline fixed.
- The retrieval-quality signal is part of the head's contract from day one — encoding the lesson from Phase 1 angle-2 probe.
- The verdict-vs-abstention distinction (Phase 2 SCOPE.md) is enforced at the orchestrator layer, not inside heads.

## Alternatives considered

- **Bake abstention into the verifier prompt.** Tempting but couples calibration to prompt-engineering and obscures the Phase 7 ablation surface.
- **Use only verifier softmax.** Misses the retrieval-quality signal. Kept as an ablation baseline.
