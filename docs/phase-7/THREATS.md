# Phase 7 — Threats to Validity

Pre-registered list of caveats keyed to the NFRs in
[../phase-2/REQUIREMENTS.md](../phase-2/REQUIREMENTS.md) and the H1
sub-hypotheses in [../phase-2/HYPOTHESES.md](../phase-2/HYPOTHESES.md). The
final report cites each item that's load-bearing for its claims.

## T-1. Single-machine evaluation

All Phase 7 numbers come from a single machine (Apple Silicon + Groq). No
cross-hardware variance check has been performed.

**Mitigation:** the cross-machine reproducibility check is Phase 11. The
NFR-Repro-1 amendment in `phase-2/REQUIREMENTS.md` already scopes
bit-identical reproducibility to the local llama-cpp path; Groq runs are
reproducible "within tolerance" only.

## T-2. Groq model-version drift mid-experiment

A long-running experiment may straddle a Groq model version bump, mixing two
model versions in the same run.

**Mitigation:** every `Verdict.metadata` record carries `model_id` +
`model_version`. The orchestrator surfaces a warning when version drift is
detected within a single run (planned Phase 9 monitor).

## T-3. Attack-set generator shares architecture with verifier

Both the paraphraser and the verifier are LLMs. A label-flipping paraphrase
would inflate the F1 drop "attack" without it being a style attack.

**Mitigation:** Phase 3 §3 NLI entailment gate (DeBERTa-v3-MNLI, p ≥ 0.7)
on every paraphrase. Failed paraphrases are dropped, not scored. Manual
spot-check on 10% of survivors planned at real-run time.

## T-4. τ-coverage coupling

Picking τ on the same set you evaluate on inflates accuracy at coverage and
biases H1.b toward "supported".

**Mitigation:** Phase 7 uses a 3-way fold split (calibration / threshold /
eval). The eval fold is the only one that produces headline numbers. See
D-702 in [phase-7-decisions.md](../phase-7-decisions.md).

## T-5. AVeriTeC v2 leaderboard not entered

Leaderboard rules require open-weights on a single 23 GB GPU; we run hosted
Groq.

**Mitigation:** we evaluate against the AVeriTeC v2 dev / test sets and
report numbers without claiming a leaderboard rank. Wording in the final
report: "evaluated using the AVeriTeC v2 data" — not "achieved place X on
the leaderboard".

## T-6. Per-topic slice n may be small

Fairness slices on AVeriTeC's topic field may have <30 examples in some
slices, which is too few for stable F1 / ECE.

**Mitigation:** the report only shows slices with `n ≥ 30` (per Phase 3 §2).
Smaller slices are documented as "n too small" in the fairness report.

## T-7. English-only

The H1 evaluation is English-only. Multilingual coverage was deferred at
Phase 1.

**Mitigation:** documented in `MODEL-CARD.md` (Phase 11) and in the report's
"Limitations" section. MuMiN-small remains a Phase 8+ stretch.

## T-8. Family-wise error inflation

H1 is a conjunction of four sub-hypotheses each tested at α=0.05; the
family-wise error is ≈ 1 − 0.95⁴ ≈ 19%.

**Mitigation:** report Holm-corrected p-values alongside raw p-values
(D-705). The H1 decision is reported under both; agreement is the
load-bearing signal.

## T-9. Synthetic smoke ≠ science

The smoke run produces well-formed reports from synthetic data. The numbers
have no scientific interpretation.

**Mitigation:** every smoke report carries a banner. Smoke output lives at
`reports/_smoke/`; the real run lives at `reports/phase7/`. The final
research report cites only the latter.

## T-10. Calibration-set construction

Calibrating on the same dataset family as the eval set risks transferring
distributional artefacts into the abstention head.

**Mitigation:** the 3-way fold uses non-overlapping subsets of the same
distribution. Cross-distribution calibration (e.g. fit on AVeriTeC, eval on
FakeNewsNet PolitiFact text) is reported as a robustness probe with the
expected drop documented.
