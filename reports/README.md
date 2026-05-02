# `reports/`

Where Phase 7 evaluation reports land. Two subdirectories matter:

- `reports/_smoke/` — produced by `misinfo phase7 --smoke`. Synthetic-data smoke output; every report carries a `[SMOKE — synthetic data, do not cite]` banner. Validated in CI by `tests/test_phase7_smoke.py`.
- `reports/phase7/` — produced by the real run (AVeriTeC v2 + LLM-paraphrase attack set, Groq backend). The final research report cites this directory.

## What each file means

| File | Reads | Owner phase |
|---|---|---|
| `h1_decision.md` | top-level supported / rejected for the H1 conjunction | 7 |
| `h1a.md` | vulnerability of the no-abstention baseline | 7 |
| `h1b.md` | F1 retention ≥ 80% with abstention at coverage 0.7 | 7 |
| `h1c.md` | ECE under attack: abstention vs no-abstention | 7 |
| `h1d.md` | abstention rate ∈ [0.10, 0.50] (anti-trivial guard) | 7 |
| `calibration.md` | per-system reliability tables | 7 |
| `risk-coverage.md` | risk vs coverage curves | 7 |
| `robustness.md` | system × condition F1 grid | 7 |
| `fairness.md` | per-topic accuracy on the clean condition | 7 |
| `error-decomposition.md` | confusion matrix for the headline system | 7 |
| `averitec-score.md` | AVeriTeC recall *proxy* (not Ev2R; documented caveat) | 7 |
| `phase7_runs.csv` | flat `(system, condition, seed) → metric` table feeding the writers | 7 |
| `runs_metadata.json` | config + τ per system | 7 |
| `cells/*.json` | per-cell `Results` dumps | 7 |

## How to reproduce

```bash
# Smoke (offline, deterministic)
misinfo phase7 --smoke --out reports/_smoke/

# Real (needs AVeriTeC + Groq)
# See docs/phase-7-evaluation.md §Run.
```
