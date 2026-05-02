# Phase 9 — Continuous Monitoring & Quality Gates

**Status:** Implemented
**Reads:** [phase-2/REQUIREMENTS.md](phase-2/REQUIREMENTS.md), [phase-8-decisions.md](phase-8-decisions.md) D-806
**Read by:** Phase 11 (release sign-off)

## What Phase 9 ships

1. **`misinfo.monitoring`** — drift snapshots + PSI, quality gates, a tiny CI orchestrator. See [src/misinfo/monitoring/](../src/misinfo/monitoring/).
2. **Frozen regression eval** — 30 deterministic synthetic claims at [tests/data/regression_frozen.jsonl](../tests/data/regression_frozen.jsonl); CI runs them on every PR.
3. **Quality gates** — YAML thresholds at [docs/phase-9/thresholds.example.yaml](phase-9/thresholds.example.yaml); `misinfo gate` exits non-zero on breach.
4. **Real Prometheus client** — Phase 8's in-process metrics swapped for `prometheus-client`; same metric names, contract preserved.
5. **Grafana stack** — opt-in via `docker compose --profile monitoring up`. Dashboard at [monitoring/grafana/provisioning/dashboards/misinfo.json](../monitoring/grafana/provisioning/dashboards/misinfo.json).
6. **CI workflow** — [.github/workflows/ci.yml](../.github/workflows/ci.yml) runs lint + tests + coverage gate (≥ 70%) + the regression-set gate. Fully offline, no Groq.
7. **Incident playbook** — [docs/runbooks/model-regression.md](runbooks/model-regression.md).

## CLI

```bash
# Snapshot a Results JSON for later drift comparison
misinfo monitor snapshot --input results.json --output snapshot.json

# Compare a reference snapshot to a live snapshot, write a markdown report
misinfo monitor drift \
  --reference reports/baseline.json \
  --live reports/live.json \
  --report reports/drift.md

# Gate a Results JSON against thresholds — exits 1 on breach
misinfo gate \
  --results results.json \
  --thresholds docs/phase-9/thresholds.example.yaml \
  --report reports/gate.md
```

## Drift detection

PSI (Population Stability Index) over four canonical features built from `Results.per_claim`:

| Feature | Kind | Why |
|---|---|---|
| `verdict` | categorical | Has the verdict mix shifted? |
| `confidence` | numeric (10 deciles) | Has the confidence distribution shifted? |
| `claim_length` | numeric (8 buckets) | Are users sending different inputs? |
| `abstain` | categorical | Has the abstention rate shifted? |

Verdict thresholds: `< 0.10` stable, `< 0.25` minor, `≥ 0.25` major. The CLI exits non-zero on `major`.

Real drift detection lights up only when a real *reference* snapshot exists. Phase 11 captures one at release time. Until then, the regression eval guards against unintended pipeline change.

## Quality gates

Operators: `le`, `ge`, `lt`, `gt`, `eq`, `spread_le`. The first five compare an aggregate metric against a threshold; `spread_le` requires `slice_metric` and bounds the per-slice spread (max − min) — the building block for NFR-Fair-1.

[thresholds.example.yaml](phase-9/thresholds.example.yaml) is the *contract example*; release-time numbers go in a release-specific thresholds file at Phase 11.

## Prometheus / Grafana

`prometheus-client` exposes the same metric names as Phase 8 plus a new `misinfo_confidence` histogram. The Grafana dashboard renders four panels: request rate, latency p95, verdict mix, verdict-confidence p50.

Bringing the stack up:

```bash
docker compose --profile monitoring up
# - app:        localhost:8000
# - langfuse:   localhost:3000
# - prometheus: localhost:9090
# - grafana:    localhost:3001  (anonymous viewer enabled)
```

Default `docker compose up` doesn't pull these — the monitoring profile is opt-in.

## CI

[.github/workflows/ci.yml](../.github/workflows/ci.yml):

- `ruff check src tests`
- `mypy src/misinfo` (advisory; existing IDE diagnostics are environment-only)
- `pytest --cov=src/misinfo --cov-fail-under=70`
- `misinfo gate` against the frozen regression set with [thresholds.example.yaml](phase-9/thresholds.example.yaml)

CI is fully offline: no Groq, no Langfuse, no real network. The `live`-marked tests stay deselected.

## Tests

| File | Cases | Covers |
|---|---|---|
| `test_drift.py` | 5 | PSI on identical / disjoint snapshots; numeric edges; report verdict; JSON round-trip |
| `test_gates.py` | 5 | each operator + spread + YAML loader |
| `test_regression_frozen.py` | 1 | CI-shape: regression set passes example thresholds |
| `test_metrics_prom.py` | 3 | prometheus-client output preserves Phase 8 metric names |
| `test_cli_monitor.py` | 4 | `gate` pass/fail, `monitor snapshot/drift` round-trips |

`pytest` → **130 passed, 1 deselected.** Coverage: 82%.

## Out of scope (deferred)

- Alertmanager / paging rules → Phase 11.
- Auth on `/metrics` → Phase 11.
- Real production-traffic drift (needs a deploy with traffic) → Phase 11.
- Promotion automation (canary / blue-green) → Phase 11.
- Retraining workflow — out of project scope (LLM frozen).
