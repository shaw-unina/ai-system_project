# ADR-0011 — Adopt `prometheus-client` for service metrics

**Status:** Accepted
**Date:** 2026-05-02
**Reads:** [0010-http-service.md](0010-http-service.md), Phase 8 D-806

## Context

Phase 8 D-806 deferred the real Prometheus client to Phase 9 with the note
"the swap is a drop-in." Phase 9 is when monitoring lands; we swap.

## Decision

Replace [src/misinfo/services/metrics.py](../../src/misinfo/services/metrics.py)
with a thin wrapper around `prometheus-client`. Public API unchanged:
`METRICS.observe_request`, `METRICS.observe_verdict`,
`METRICS.render_prometheus`, `METRICS.reset`. Same metric names so the Phase 8
endpoint contract is preserved.

A new `misinfo_confidence` histogram lets the Grafana dashboard render
verdict-confidence percentiles over time.

## Consequences

- `prometheus-client` joins the `[service]` extras in `pyproject.toml`. Phase 5–7 contributors who don't install `[service]` are unaffected.
- One Phase 8 test required a one-character change (`int(...)` → `float(...)` when parsing the counter line) because prometheus-client emits `3.0` rather than `3`. The contract — same metric *names* — held.
- Phase 9 Grafana dashboard works out-of-the-box because the standard exposition format is what `prometheus-client` produces.

## Alternatives considered

- **Keep the in-process store.** Rejected: Phase 9's whole point is real monitoring, and reinventing histogram quantile estimation and label cardinality bookkeeping is busywork.
- **OpenTelemetry metrics.** Promising but heavier: needs an exporter, a collector, and decisions we don't need to make until Phase 11.
