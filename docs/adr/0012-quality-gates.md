# ADR-0012 — Quality gates: YAML-driven, CLI-runnable, slice-aware

**Status:** Accepted
**Date:** 2026-05-02

## Context

Phase 9 needs a way to *gate promotion* on metric thresholds: "this PR drops
accuracy past floor X" should fail CI; "this release violates the fairness
spread bound" should block sign-off.

## Decision

A YAML thresholds file is the source of truth. Each gate is one row:

```yaml
gates:
  - name: <unique>
    metric: <aggregate_field> | slice_metric: <slice_field>
    op: le | ge | lt | gt | eq | spread_le
    value: <float>
```

`spread_le` is the fairness operator: `max(slice_metric) − min(slice_metric)
≤ value`. The other operators compare an aggregate metric directly.

`misinfo gate --results <results.json> --thresholds <file.yaml>` exits 0 if
all gates pass, 1 otherwise. CI invokes this directly.

## Consequences

- Adding a new metric: extend `AggregateMetrics` (existing path) and reference
  it by name in YAML. No code changes in `gates.py`.
- Per-environment thresholds: copy and tighten. The example file
  ([docs/phase-9/thresholds.example.yaml](../phase-9/thresholds.example.yaml))
  documents the contract; release-time thresholds live alongside the release.
- A breached gate produces a markdown report listing the breached gate, its
  observed value, the target, and a one-line reason. The report is what oncall
  attaches to the incident ticket.

## Alternatives considered

- **Hard-coded thresholds in Python.** Rejected — release-time threshold tuning would require a code change and a redeploy.
- **JSON Schema.** Rejected as overkill for a 5-field row.
- **Pydantic-driven config.** Considered; current dataclass + small validator is enough. Promote to Pydantic if the YAML grows.
