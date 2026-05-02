# Runbook — Model regression

How to respond when a Phase 9 quality gate fires. Each section lists the
gate, the symptom on call, what to check first, and when to escalate.

> Where this runbook says "the gates report," it means the markdown
> produced by `misinfo gate --report ...` and attached to the alert.

## 1. `accuracy_floor` breached

**Symptom:** CI failed; gates report shows accuracy on the regression /
release set is below the floor.

**Check first (in order):**

1. Did this run use the right backend? `Verdict.metadata.backend` should be
   the one expected for the environment.
2. Did the model version drift? Compare `Verdict.metadata.model_version`
   across the failed run and the last passing run.
3. Did a prompt change land? Inspect recent commits to
   [src/misinfo/pipeline/prompts/](../../src/misinfo/pipeline/prompts/).
4. Did retrieval change? Look at `mean_top1` / `evidence_coverage` on
   `ClaimResult.signals`; a sudden drop signals a retrieval-side issue.
5. Roll back the offending PR if the regression is large; otherwise open a
   ticket and downgrade the alarm to a tracked task.

**Escalate** if accuracy drop > 5 abs pts vs the last passing run **and**
the cause isn't obvious from steps 1–4.

## 2. `ece_ceiling` breached

**Symptom:** Calibration metric exceeded its ceiling.

**Check first:**

1. Has the abstention head been re-fit recently? A stale calibration head on
   a new verifier model often spikes ECE.
2. Look at the reliability table in
   [reports/calibration.md](../../reports/calibration.md) (Phase 7 artefact)
   to see *which* bins drifted.
3. Re-run the Phase 6 calibration pipeline on the latest dev set; the head
   under-fits if calibration data is stale.

**Escalate** if re-fitting the head doesn't recover ECE within 0.05 of the
ceiling.

## 3. `abstention_band_*` breached

**Symptom:** Abstention rate fell outside `[0.10, 0.50]` (the H1.d band).

**Check first:**

- **Below 0.10:** τ is set too low (the system trusts the verifier too much)
  or retrieval is unusually strong on this set. Re-run
  `misinfo abstention threshold` against the threshold fold to pick a fresh τ.
- **Above 0.50:** τ is too high; the system is abstaining trivially. Same
  remediation: re-pick τ.

**Escalate** if no τ in `[0.05, 0.95]` lands the rate inside the band — that
indicates a retrieval pipeline issue, not a calibration one.

## 4. `fairness_spread` breached

**Symptom:** Per-slice F1 spread exceeded the bound.

**Check first:**

1. Which slice is the outlier? The gates report names it.
2. Is the outlier slice small (n < 30)? Small slices have noisy F1; document
   the noise and lower the bound at next release if appropriate.
3. Is one topic dominating training-time prompt iteration? Phase 6 head
   re-fit usually fixes this.

**Escalate** if the spread persists across two consecutive releases — that's
a Phase 10 / dataset-cards problem, not a Phase 9 one.

## 5. Drift major (PSI ≥ 0.25)

**Symptom:** `misinfo monitor drift` reports `overall: major`.

**Check first:**

1. Which feature drifted? `verdict`, `confidence`, `claim_length`, `abstain`?
2. Did the upstream traffic change (deployment, marketing campaign, partner
   integration)? `claim_length` drift usually points there.
3. Did the model change? `verdict` and `confidence` drift usually do.
4. If the reference snapshot is older than 30 days, refresh it — the
   distribution moved legitimately and the snapshot is now stale.

**Escalate** if the drift coincides with an `accuracy_floor` or
`ece_ceiling` breach in the same window — that's a real regression, not a
distribution shift.
