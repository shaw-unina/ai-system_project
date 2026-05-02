# Phase 9 — Decisions

ADR-style summary of what landed in Phase 9. The full plan is in
[phase-9-monitoring.md](phase-9-monitoring.md); the binding ADRs are
[adr/0011-prometheus-client.md](adr/0011-prometheus-client.md) and
[adr/0012-quality-gates.md](adr/0012-quality-gates.md).

## D-901. PSI for drift, not KL/Wasserstein

PSI is the standard model-monitoring metric in industry; thresholds (0.10 /
0.25) are well-understood. Wasserstein needs sklearn, KL is touchy at zero.

## D-902. Drift snapshots are JSON, not parquet

Snapshots are tiny (≤ a few KB). JSON keeps the on-disk format diff-able and
the loader trivial. Phase 11 can revisit if we need archive-grade artefacts.

## D-903. Frozen synthetic regression set

Real headline numbers are deferred (Groq + AVeriTeC). The frozen set
guarantees that *unintended pipeline changes* are caught in CI without
external dependencies. It's deliberately small (30 claims) so CI is fast.

## D-904. `misinfo gate` exit code

Non-zero on any breach. CI uses this directly; no glue script required.
`spread_le` is the only multi-input operator (needs the slices on `Results`).

## D-905. Prometheus-client swap, contract preserved

Same metric names. The Phase 8 endpoint test remained valid except for one
character (`int` → `float` parse, since prometheus-client emits `3.0` rather
than `3`). Documented in [ADR-0011](adr/0011-prometheus-client.md).

## D-906. Confidence histogram added

`misinfo_confidence` (10 buckets) lets the Grafana dashboard render
verdict-confidence p50 over time — a leading indicator for upcoming
calibration drift before the gate fires.

## D-907. Monitoring stack is opt-in (Compose profile)

Default `docker compose up` doesn't pull Prometheus + Grafana. Operators who
want them run `docker compose --profile monitoring up`. Keeps the dev-loop
fast for Phase 5–8 contributors.

## D-908. Grafana on 3001, not 3000

Langfuse already binds 3000. Avoiding port collision keeps `docker compose
up --profile monitoring` working out-of-the-box.

## D-909. CI mypy advisory until Phase 11

The codebase has IDE-environment-driven type warnings (system-Python-vs-conda
mismatch); making mypy hard-fail in CI now would cause spurious red builds.
We capture the output but `continue-on-error: true`. Phase 11 lands strict
typing as part of release sign-off.

## D-910. Coverage gate at 70% (we're at 82%)

Generous headroom prevents brittle test churn from breaking unrelated PRs;
real coverage drift is still flagged on the PR diff.

## Coverage at Phase 9 close

`pytest` → **130 passed, 1 deselected**. Coverage: 82% on `src/misinfo/`.
The new `monitoring/` package and the swapped `services/metrics.py` ship
with their own tests; the Phase 8 API tests continue to pass against the
prometheus-client backend.
