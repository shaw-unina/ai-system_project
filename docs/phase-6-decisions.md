# Phase 6 — Decisions

ADR-style summary of what landed in Phase 6. The full plan is in
[phase-6-proposed-method.md](phase-6-proposed-method.md); the head-selection
rationale is in [adr/0009-abstention-heads.md](adr/0009-abstention-heads.md).

## D-601. Four concrete heads + Identity control

Shipped: `TemperatureScalingHead`, `IsotonicCalibrationHead`,
`RetrievalGatedHead`, `LogisticFusionHead`. `IdentityAbstentionHead` retained
as the Phase 7 control variable. Conformal head deferred (no schedule pressure
to land it; the four primary heads cover the H1 design space).

## D-602. Orchestrator owns τ

Per ADR-0007, the head returns calibrated `(label, confidence)` and never
"Abstain"; the orchestrator applies `confidence < tau → "Abstain"`. Keeps the
head's contract pure and lets Phase 7 sweep τ without re-fitting heads.

## D-603. CalibrationRecord schema

Verifier confidence + `mean_top1` + `evidence_coverage` + `correct`. Same JSONL
format consumed by `misinfo calibrate` and producible from `Results.per_claim`
once `ClaimResult.signals` is populated by the harness.

## D-604. Persistence formats

JSON for heads with a small numeric state (`Temperature`, `RetrievalGated`).
Joblib for sklearn-backed heads (`Isotonic`, `Fusion`). Default location:
`models/abstention/<head>.{json,joblib}` — gitignored.

Why mix formats: JSON stays diff-readable for the cheap heads (so a reviewer
can inspect `temperature: 1.7`); joblib is the canonical sklearn round-trip
path for fitted estimators.

## D-605. sklearn lazy-imports

Both `Isotonic` and `Fusion` defer `import sklearn.*` until `fit()` / `load()`.
The orchestrator can construct any head without paying the sklearn import cost
when it's not needed. Verified by `python -c "import misinfo.abstention.fusion"`
in the conda env: no sklearn import triggered.

## D-606. CLI factchecker builder factored

`_build_factchecker(corpus, head_name, head_path, tau)` is the single wiring
point used by `verify` / `batch` / `eval`. The Phase 5 helper
`_build_factchecker_from_corpus` is kept as a thin wrapper so existing tests
stay unchanged.

## D-607. Test isolation strategy

Every Phase 6 head test uses NumPy-synthesised `CalibrationRecord` lists; no
Groq / Langfuse calls. The orchestrator τ-override test uses MockBackend with a
scripted response factory. Live calibration on real Groq output is exercised
manually via the existing cache + `misinfo calibrate` round-trip; the workflow
is documented in [phase-6-proposed-method.md](phase-6-proposed-method.md).

## D-608. Phase 7 ablation surface

The five heads (Identity, Temperature, Isotonic, RetrievalGated, Fusion) ×
multiple τ operating points = the Phase 7 grid. The `--target-coverage` flag
on `misinfo eval` lets Phase 7 fix coverage at 0.7 (per H1.b) and compare F1
retention across heads.

## Coverage at Phase 6 close

`pytest` → **79 passed, 1 deselected**. Coverage on `src/misinfo/` should be
roughly stable vs Phase 5 (~73%); the new abstention modules ship with their
own tests, the orchestrator τ branch is exercised by
`test_orchestrator_abstain.py`.
