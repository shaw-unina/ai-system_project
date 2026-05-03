# Operator Guide

Day-to-day operations for the misinfo service + dashboard. Pairs with the
runbooks in [runbooks/](runbooks/).

## Deployment

```bash
git clone … && cd project
cp .env.example .env
# Fill in MISINFO_API_KEYS, OPERATOR_PASSWORD, BACKEND_API_KEY,
# BACKEND_METRICS_TOKEN, GROQ_API_KEY (or set MISINFO_BACKEND=llama_cpp).
docker compose up -d --build
docker compose --profile monitoring up -d
```

Surfaces:

| URL | What |
|---|---|
| `http://localhost:8000/healthz` | liveness |
| `http://localhost:8000/readyz` | readiness |
| `http://localhost:8000/metrics` | Prometheus exposition (token-gated if configured) |
| `http://localhost:3002/verify` | end-user claim submission |
| `http://localhost:3002/operator` | operator dashboard (password-gated) |
| `http://localhost:3001` | Grafana |

## Auth

- **API:** bearer tokens listed in `MISINFO_API_KEYS` (comma-separated).
  Empty = auth disabled (local dev only).
- **Dashboard:** single shared password in `OPERATOR_PASSWORD`. Empty =
  open. The frontend's API proxy injects `BACKEND_API_KEY` server-side; the
  browser never sees it.
- **Metrics scraping:** `MISINFO_METRICS_TOKEN` if set; Prometheus scrape
  config in [monitoring/prometheus.yml](../monitoring/prometheus.yml)
  needs the matching bearer token.

## Rotating API keys

1. Generate a new key: `openssl rand -hex 32`.
2. Append to `MISINFO_API_KEYS` (keep the old one).
3. `docker compose up -d app` to apply.
4. Update `BACKEND_API_KEY` on the frontend service; redeploy.
5. Once all clients are migrated, remove the old key and redeploy `app`.

## Choosing a retriever

`MISINFO_RETRIEVER=web` (default) calls Tavily live for every
sub-question — broad coverage, ~$0.005 per claim, non-deterministic.
Requires `SEARCH_API_KEY`.

`MISINFO_RETRIEVER=bm25` retrieves over a fixed corpus selected by
`MISINFO_CORPUS_PROFILE` (or `MISINFO_CORPUS_PATH` for a custom JSONL).
Built profiles live in `data/processed/<profile>_corpus.jsonl`. Build
with:

```bash
python scripts/build_corpus.py averitec    # ~6k docs from AVeriTeC v2
python scripts/build_corpus.py wiki --max 50000   # Simple-English Wikipedia leads
python scripts/build_corpus.py union       # both, deduped
```

Use `bm25` + `averitec` to reproduce the Phase 7 metrics in MODEL-CARD.

## Second-opinion sidecar

Set `GOOGLE_FACT_CHECK_API_KEY` to surface third-party fact-checks on
the verify page. Disabled-by-default; the dashboard renders a one-line
"disabled" state otherwise. Results are cached server-side for 24h to
bound API cost.

## Watching Grafana

The Phase 9 dashboard (`monitoring/grafana/provisioning/dashboards/`)
covers:

- Request rate by endpoint / status.
- Latency p50 / p95 (target: ≤ 30 s / 60 s).
- Verdict mix (proportion of `Abstain`).
- Error rate (5xx).

## Responding to a regression-gate failure

The CI quality gate (Phase 9) runs `python -m misinfo.cli gate` on a
frozen regression set. If it fails:

1. Fetch `regression_results.json` from the failed CI run.
2. Compare against the prior tag's results (committed under
   `reports/phase9/regression-*.json`).
3. If the regression is real and intentional (e.g., new model), update
   `docs/phase-9/thresholds.example.yaml` in a follow-up PR; never just
   skip the gate.
4. If unintentional, bisect with `git bisect` against the gate command.

## Responding to a perf budget miss

If `make perf-latency` reports p95 > 60 s:

1. Check Grafana for upstream LLM latency (Groq tail).
2. Check `/readyz` — backend / head / τ should match the deployed config.
3. Re-run on `MISINFO_BACKEND=llama_cpp` to isolate provider variability.
4. If genuinely a code regression, `git bisect run make perf-latency`.

## Draining low-confidence rows

If `MISINFO_LOWCONF_PERSIST=true`, low-confidence verdicts are stored in
`data/lowconf.db` (SQLite). Operator workflow:

1. Open `/operator`, review the table, export as CSV.
2. Triage flagged claims with a human reviewer.
3. Clear the table from the dashboard (clears the SQLite rows for that
   API key).

## Releasing a new version

Short version:

```bash
# from main, fully merged from dev
git tag -a v1.0.0 -m "v1.0.0"
git push --tags
# CI release.yml builds + signs + publishes images,
# attaches SBOM to the GitHub Release.
```

Then update the README's "latest release" line manually.
