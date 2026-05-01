# Phase 1 — Research Scouting (artifacts)

This folder contains the deliverables of Phase 1, executed against the plan in [../phase-1-research-scouting.md](../phase-1-research-scouting.md).

## Layout

```
phase-1/
├── README.md                  this file
├── literature-matrix.csv      30+ paper survey, the input to angle selection
├── probes/                    design + (when run) results of week-2 probes
│   ├── angle-1-llm-fakes.md           robustness to LLM-generated misinformation
│   ├── angle-2-retrieval-failure.md   retrieval-quality + abstention
│   └── angle-4-calibration.md         calibrated selective prediction
├── DECISION.md                the chosen angle, with rejected alternatives
└── professor-signoff.md       record of professor approval (filled after office hours)
```

## How the artifacts relate

1. The **literature matrix** is the evidence base. Every claim in `DECISION.md` traces back to rows here.
2. The **probes** are short, falsifiable empirical tests of the most promising angles. They exist to surface the failure mode in numbers, not to solve it.
3. **`DECISION.md`** is the single deliverable that ends Phase 1 and starts Phase 2. It selects one angle and explicitly records the rejected alternatives — this becomes the "Current solutions and limitations" of the final research report.

## Running the probes

Probes are designed to be runnable in **half a day each** on a single consumer GPU (or Colab Pro) using Phase 0 utilities (`misinfo.config`, `misinfo.repro`, `misinfo.logging`). The probe write-ups in `probes/` contain the full experimental spec; the `notebooks/phase-1/` folder is where the actual runs live.

If a probe is design-only (not yet executed), the file is clearly marked `Status: DESIGN` at the top.

## Status legend (used in probe files)

- `DESIGN` — spec written, not yet run.
- `IN PROGRESS` — code exists, partial results.
- `DONE` — results table populated, conclusions drawn.

## Exit criteria recap

All four must be met before Phase 2:
- ≥ 30 entries in `literature-matrix.csv`, ≥ 60% from 2024–2026.
- ≥ 3 probes have measured the failure mode they target.
- `DECISION.md` committed on `dev`.
- `professor-signoff.md` populated.
