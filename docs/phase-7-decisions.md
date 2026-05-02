# Phase 7 — Decisions

ADR-style summary of what landed in Phase 7. The full plan is in
[phase-7-evaluation.md](phase-7-evaluation.md); threats are in
[phase-7/THREATS.md](phase-7/THREATS.md).

## D-701. Smoke-only execution

Phase 7 ships the harness + statistical machinery + report templates,
exercised end-to-end on synthetic data + MockBackend. The real AVeriTeC +
Groq run is deferred to a separate task.

**Why:** mirrors the Phase 5 / 6 pattern, keeps CI clean and reviewable,
avoids burning Groq quota during code review. The harness change cost from
"smoke" to "real" is one branch in `run_phase7`.

## D-702. 3-way fold split

Calibration / threshold / eval folds, deterministic shuffle keyed on the
project seed. Avoids the τ-coverage double-dip flagged in Phase 6 D-503.

**Why:** picking τ on the same set you evaluate on inflates accuracy at
coverage; a held-out threshold fold is the standard fix.

## D-703. NumPy paired bootstrap

`paired_bootstrap_diff(metric_fn, y_true, y_a, y_b)` operates on the label
arrays — not on Verdict objects — so a 10 000-resample bootstrap on 500
claims runs in seconds. One-sided p-values for H1.a / H1.b; two-sided CI for
H1.c.

**Why:** vectorising over claim indices is enough; the heavy work is the
metric eval, which is already O(n) per resample.

## D-704. Smoke banner on every report

Every report rendered from a smoke run prepends a
`[SMOKE — synthetic data, do not cite]` banner. The real run drops it.

**Why:** the rubric expects publishable reports under `reports/`. We don't
want a future reader to mistake the smoke output for findings.

## D-705. Holm correction for H1 family

H1 decomposes into four sub-hypotheses; running each at α=0.05 inflates
family-wise error to ~19%. We report Holm-corrected p-values alongside the
raw ones.

**Why:** standard practice for a small, pre-registered family of tests.

## D-706. AVeriTeC recall as a *proxy*

The success-criteria matrix has a `reports/averitec-score.md` row but the
official Ev2R metric needs reference QA pairs we don't have. We report the
existing `averitec_recall_proxy` from `eval/metrics.py` and document the
caveat in the report itself.

**Why:** scoping; the official metric requires data infrastructure beyond
Phase 7.

## D-707. Pure-Python report writers

No matplotlib in the smoke path. Reliability bins, risk-coverage curves,
confusion matrices, fairness slices all render as markdown tables. A future
real-run can drop in matplotlib for PNG plots without changing the writer
signatures.

**Why:** keeps the `inference` extra slim and CI deterministic. Adding mpl
is one optional-deps line.

## D-708. Topic slice via the synthetic claim suffix

The smoke generator embeds the topic in the claim text (`"... about
politics"`); the fairness writer parses that out. Real runs read `topic`
from the AVeriTeC row directly, via the existing `eval/slices.by_field`
helper.

**Why:** keeps the smoke fixture self-contained without mocking Phase 3 data
schemas.

## Coverage at Phase 7 close

`pytest` → **94 passed, 1 deselected** (live). Coverage stays ≥ 70% on
`src/misinfo/`. The 4 new eval modules (`bootstrap`, `folds`, `reliability`,
`phase7`, `decisions`, `reports_phase7`) ship with their own tests; the
phase-7-specific `cli.py` branch is exercised by
`tests/test_phase7_smoke.py` indirectly.
