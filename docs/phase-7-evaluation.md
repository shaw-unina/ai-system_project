# Phase 7 — Evaluation & Trustworthiness Assessment

**Status:** Implemented (smoke). The real run produces headline numbers and is documented below.
**Reads:** [phase-2/HYPOTHESES.md](phase-2/HYPOTHESES.md), [phase-2/SUCCESS-CRITERIA.md](phase-2/SUCCESS-CRITERIA.md), [phase-6-proposed-method.md](phase-6-proposed-method.md)
**Read by:** Phase 11 (release sign-off), the final research report

## What Phase 7 ships

A fully-wired evaluation harness that turns Phases 5–6 into the trustworthiness reports the success-criteria matrix demands. The harness is exercised end-to-end on synthetic data + MockBackend (the *smoke* path); the real run that produces publishable numbers is parameter-only and documented in §Run.

Concretely:

- **Statistical primitives.** Paired bootstrap (CI + one-sided p-value), 95% CI bootstrap, Holm correction. Pure NumPy. See [src/misinfo/eval/bootstrap.py](../src/misinfo/eval/bootstrap.py).
- **3-way fold splitter** (calibration / threshold / eval) — avoids τ-coverage double-dipping per the Phase 6 risk note. See [src/misinfo/eval/folds.py](../src/misinfo/eval/folds.py).
- **Reliability + risk-coverage primitives** — [src/misinfo/eval/reliability.py](../src/misinfo/eval/reliability.py).
- **Phase 7 orchestrator.** Calibrates each abstention head, picks τ, evaluates every (system × condition × seed) cell, writes per-cell `Results` JSON + a single `phase7_runs.csv` summary. See [src/misinfo/eval/phase7.py](../src/misinfo/eval/phase7.py).
- **H1 decision logic.** `decide_h1(runs) → H1Decision` runs H1.a–d with the rejection thresholds from `HYPOTHESES.md`. See [src/misinfo/eval/decisions.py](../src/misinfo/eval/decisions.py).
- **Report writers.** One markdown writer per success-criteria row: `h1a–d.md`, `calibration.md`, `risk-coverage.md`, `robustness.md`, `fairness.md`, `error-decomposition.md`, `averitec-score.md`, plus a top-level `h1_decision.md`. See [src/misinfo/eval/reports_phase7.py](../src/misinfo/eval/reports_phase7.py).
- **CLI.** `misinfo phase7 run --smoke --out reports/_smoke/` produces every report end-to-end without touching Groq.

## Run

### Smoke (offline, default)

```bash
misinfo phase7 --smoke --out reports/_smoke/
```

Produces 5 systems × 4 conditions × 3 seeds = 60 cells (default config) on synthetic data with `MockBackend`. Smoke reports carry a `[SMOKE — synthetic data, do not cite]` banner. The smoke path is the only mode validated in CI; it exercises the full machinery and verifies report shape.

### Real (deferred — needs AVeriTeC + Groq budget)

The real run is documented but not executed in this phase. The procedure:

1. Download AVeriTeC v2 dev (Phase 3 loaders): `misinfo data download averitec --version v2`.
2. Generate the LLM-paraphrase attack set (Phase 3 generator): `misinfo data attack-set --src averitec/v2/dev --styles newswire,tabloid,social`.
3. Replace the smoke synthetic-data path in `phase7.run_phase7` with a non-smoke branch that loads dev + attack JSONL and constructs `RAGFactChecker` against `GroqBackend` (the file cache from Phase 5 makes reruns offline).
4. `misinfo phase7 --out reports/phase7/ --limit <N>` writes the publishable reports.

The Phase 5 response cache (`<data_dir>/cache/`) makes the second run free; the first pass is the only one that hits Groq. This is the file the final research report cites.

## Outputs

```
<out>/
├── cells/<system>__<condition>__seed<k>.json   # per-cell Results dump
├── phase7_runs.csv                              # cell × headline metric summary
├── runs_metadata.json                           # config + τ_by_system
├── h1a.md, h1b.md, h1c.md, h1d.md
├── h1_decision.md                               # top-level supported|rejected
├── calibration.md                               # reliability tables per system
├── risk-coverage.md
├── robustness.md
├── fairness.md
├── error-decomposition.md
└── averitec-score.md
```

Every report writer is a pure function of the runs object — re-running with the same seeds produces bit-identical markdown.

## Threats to validity

See [phase-7/THREATS.md](phase-7/THREATS.md). The pre-registered list keys to NFR-Trans / NFR-Rob and the Phase 6 τ-coverage caveat.

## Tests (offline, MockBackend)

- `test_bootstrap.py` — paired bootstrap zeroes on identical predictions; p-value monotone in effect size; seed determinism; Holm correction.
- `test_folds.py` — partition + disjoint + determinism.
- `test_reliability.py` — empty-input handling; well-calibrated synthetic.
- `test_phase7_smoke.py` — full E2E: 16-cell smoke run renders every report; summary CSV well-formed; real-run path raises `NotImplementedError`.

`pytest` → 94 passed, 1 deselected (live).

## Out of scope (deferred)

- The real, headline run (separate task; see §Run).
- Latency / throughput numbers (NFR-Lat-1, NFR-Tput) → Phase 8.
- Quality gates / CI thresholds on metrics → Phase 9.
- Cross-machine reproducibility check → Phase 11.
