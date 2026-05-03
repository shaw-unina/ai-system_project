# Phase 11 — Performance reports

Reports in this directory are produced by `scripts/perf_bench.py` against a
live FastAPI service. They are *not* generated in CI — variability across
runners makes the numbers misleading. Generate them locally before tagging a
release:

```bash
# In one shell:
docker compose up app

# In another:
export MISINFO_API_KEY=...   # if MISINFO_API_KEYS is configured
make perf-latency
make perf-throughput
make perf-memory
```

Outputs land in `perf-latency.md`, `perf-throughput.md`, `perf-memory.md` and
should be committed alongside the release tag.

## Budgets (from REQUIREMENTS.md)

| Metric | Budget |
|---|---|
| p50 single-claim latency | ≤ 30 s (NFR-Lat-1) |
| p95 single-claim latency | ≤ 60 s |
| Sustained throughput | ≥ 10 claims/min (NFR-Tput) |

If a run misses a budget, the release is gated until the regression is
investigated. See `docs/OPERATOR-GUIDE.md` for the runbook.
