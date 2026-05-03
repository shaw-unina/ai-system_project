# Misinformation Detector

A closed-book misinformation verification system. Submit a short factual claim;
the system decomposes it into sub-questions, retrieves evidence (live web
search by default, or a local BM25 corpus), asks an LLM to score each piece
of evidence, aggregates into a calibrated verdict — **Supported**, **Refuted**,
**Not enough evidence**, or **Abstain** — and returns a rationale, the
supporting evidence, and a confidence score the system is willing to defend.

Built for the AI Systems Engineering course (Prof. Pietrantuono) as an
end-to-end demonstration of how a research idea becomes a deployable,
observable, auditable service.

---

## Highlights

- **Closed-book RAG pipeline** — decompose → retrieve → answer → aggregate, with a calibrated abstention head that says "I don't know" when evidence is thin.
- **Live web retrieval** by default (Tavily), with a switchable BM25 fallback over a local corpus (AVeriTeC, Wikipedia, or a small smoke set) for reproducible runs.
- **Second-opinion sidecar** — Google Fact Check Tools results shown alongside the verdict for context (display-only; never feeds the pipeline).
- **FastAPI service** — `/v1/verify`, `/v1/batch`, `/healthz`, `/metrics`, with bearer-token auth, per-key sliding-window rate limiting, and prompt-injection mitigations.
- **Next.js 15 dashboard** — `/verify` for end users and `/operator` for live metrics, evaluation reports, and recent low-confidence cases. Light + dark mode, keyboard accessible.
- **Observability** — Langfuse traces for LLM calls, Prometheus metrics for service health, Grafana dashboards in compose.
- **CI/CD** — lint, typecheck, pytest, vitest, build, OpenAPI→TS drift check, advisory `pip-audit` / `npm audit` / `gitleaks`. Tagged releases publish cosign-signed images with SPDX SBOMs to GHCR.
- **Documentation as a deliverable** — model card, evaluation report, operator guide, architecture overview, limitations, and 19 ADRs covering the load-bearing decisions.

---

## Architecture at a glance

```
                        ┌──────────────────┐
   user claim  ──▶      │  /verify (Next)  │
                        └────────┬─────────┘
                                 │ proxy + auth
                        ┌────────▼─────────┐
                        │  FastAPI service │
                        │  /v1/verify      │
                        └────────┬─────────┘
                                 │
       ┌─────────────────────────┼─────────────────────────┐
       │                         │                         │
┌──────▼──────┐         ┌────────▼────────┐        ┌───────▼────────┐
│ Decompose   │         │  Retrieve       │        │   Aggregate    │
│ (LLM)       │         │  Web (Tavily)   │        │   (LLM)        │
└──────┬──────┘         │  or BM25 corpus │        └───────┬────────┘
       │                └────────┬────────┘                │
       └──────► sub-questions ───┴────► evidence ──────────┘
                                                            │
                                              ┌─────────────▼──────────────┐
                                              │  Calibrated abstention     │
                                              │  → verdict + confidence    │
                                              └─────────────┬──────────────┘
                                                            │
                                              ┌─────────────▼──────────────┐
                                              │  /v1/second-opinion        │
                                              │  (Google FC, display-only) │
                                              └────────────────────────────┘
```

Full diagram and rationale: [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

---

## Quickstart — local dev

### 1. Backend (Python)

```bash
conda env create -f environment.yml
conda activate misinfo
cp .env.example .env       # then fill in API keys (see "Configuration")
pytest -q                  # 22 tests should pass
misinfo serve --host 127.0.0.1 --port 8000
```

The package installs in editable mode via `environment.yml` — `import misinfo`
works from anywhere once the env is active.

### 2. Frontend (Next.js)

```bash
cd frontend
npm install
npm run dev                # http://localhost:3002
```

Submit a claim on `/verify`; check live service health on `/operator`.

### 3. Full stack (Docker Compose)

```bash
docker compose up --build
```

Brings up:

| Service    | Port | What                                          |
|------------|------|-----------------------------------------------|
| `app`      | 8000 | FastAPI verification service                  |
| `frontend` | 3002 | Next.js dashboard                             |
| `langfuse` | 3000 | LLM trace UI                                  |
| `grafana`  | 3001 | Metrics dashboards (Prometheus-backed)        |
| `prometheus` | 9090 | Scrape target for `/metrics`                |

---

## Configuration

`.env` is loaded by `misinfo.config.get_settings()`; never commit it.

| Variable                        | Default                  | Purpose                                                             |
|---------------------------------|--------------------------|---------------------------------------------------------------------|
| `GROQ_API_KEY`                  | —                        | LLM provider for decompose / answer / aggregate.                    |
| `MISINFO_MODEL_ID`              | `llama-3.3-70b-versatile`| Default model.                                                      |
| `MISINFO_RETRIEVER`             | `web`                    | `web` (Tavily) or `bm25` (local corpus).                            |
| `SEARCH_API_KEY`                | —                        | Tavily key when `MISINFO_RETRIEVER=web`.                            |
| `MISINFO_CORPUS_PROFILE`        | `smoke`                  | `smoke`, `averitec`, `wiki`, or `union` (used when retriever=bm25). |
| `GOOGLE_FACT_CHECK_API_KEY`     | —                        | Enables the second-opinion sidecar; leave empty to disable.         |
| `LANGFUSE_PUBLIC_KEY` / `_SECRET_KEY` / `_HOST` | —        | LLM trace export.                                                   |
| `MISINFO_API_KEYS`              | empty (auth disabled)    | Comma-separated bearer tokens accepted on `/v1/*`.                  |
| `BACKEND_API_KEY`               | —                        | Token the Next proxy injects when calling FastAPI.                  |
| `MISINFO_METRICS_TOKEN`         | empty                    | Token-gates `/metrics` if set.                                      |
| `BACKEND_METRICS_TOKEN`         | —                        | Token the Next proxy uses for `/metrics`.                           |
| `MISINFO_RATE_LIMIT_PER_MIN`    | `60`                     | Per-key sliding-window limit.                                       |
| `OPERATOR_PASSWORD`             | empty (gate disabled)    | Cookie gate for `/operator`.                                        |

`.env.example` holds the canonical list. Operator-side reference:
[docs/OPERATOR-GUIDE.md](docs/OPERATOR-GUIDE.md).

---

## How verification works

For each claim:

1. **Decompose** — the LLM produces 3–5 atomic sub-questions whose answers, taken together, decide the claim. (`prompts/decompose.txt`)
2. **Retrieve** — each sub-question is searched independently. The web retriever calls Tavily; the BM25 retriever scores against a local Whoosh-indexed corpus.
3. **Answer** — the LLM scores each piece of retrieved evidence against its sub-question, returning a per-sub-question confidence.
4. **Aggregate** — the LLM combines sub-answers into a single verdict + rationale, citing the evidence by source ID. (`prompts/aggregate.txt`)
5. **Calibrated abstention** — the aggregated raw confidence is passed through a Phase-6 calibrated head; if it falls below τ, the verdict is rewritten to `Abstain` with the reasons exposed in the rationale.
6. **Second opinion** (display-only) — the dashboard separately calls `/v1/second-opinion`, which queries Google Fact Check Tools with progressive query shortening (full claim → first sentence → first 8 words) and renders the results next to the verdict for context. These never feed the verify pipeline.

Outputs always include: verdict, confidence, evidence list with source URLs and per-span scores, rationale, low-confidence flag, request ID, model ID, and (when enabled) Langfuse trace ID.

---

## Frontend dashboard

Two surfaces, one design system:

- **`/verify`** — claim textarea, animated confidence dial, verdict chip with semantic color and icon, rationale rendered as Markdown, evidence list with show-more, "Other fact-checkers say" sidecar with Google attribution.
- **`/operator`** — KPI tiles (requests, median latency, slowest 5%, average), recent latency sparkline, verdict-mix bar chart, evaluation report list, recent low-confidence cases (held in browser session only).

Dark + light mode via `next-themes` (system default, manual toggle in nav).
Editorial typography (Newsreader display, Roboto UI), shadcn-style HSL token
system, semantic verdict palette that adapts to both themes. Design rationale:
[docs/adr/0019-design-system.md](docs/adr/0019-design-system.md).

---

## Tests

| Suite     | Command                                  | Count       |
|-----------|------------------------------------------|-------------|
| Backend   | `pytest -q`                              | 22 tests    |
| Frontend  | `cd frontend && npm run test -- --run`   | 18 tests    |
| E2E       | `cd frontend && npm run e2e`             | tag-only CI |

Backend covers the pipeline (decompose, retrieve, aggregate), the calibrated
abstention head, the FastAPI service, prompt-injection sanitisation, bearer
auth + rate limiting, and the second-opinion sidecar. Frontend covers the
verdict card, confidence dial, disclosure badge popover, low-confidence
session table, second-opinion card, and the metrics parser.

---

## Operations

- **Auth** — set `MISINFO_API_KEYS` to a comma-separated allowlist of bearer tokens. Empty = unauthenticated (local dev only).
- **Rate limit** — `MISINFO_RATE_LIMIT_PER_MIN` per token, sliding-window, in-process.
- **Metrics** — `/metrics` exposes Prometheus text. Token-gate with `MISINFO_METRICS_TOKEN`.
- **Operator gate** — `/operator` is cookie-gated by `OPERATOR_PASSWORD`. Empty = open (local dev only).
- **Security headers** — Next middleware sets CSP, HSTS (prod), X-Frame-Options, X-Content-Type-Options, Referrer-Policy.

Threat model and review: [docs/phase-11-security-review.md](docs/phase-11-security-review.md).

---

## Releases

- Push a tag `vX.Y.Z` → `release.yml` builds backend + frontend images, signs with cosign keyless (GitHub OIDC), attaches SPDX SBOMs (syft), publishes to GHCR.
- Verify a release: `cosign verify ghcr.io/OWNER/misinfo:vX.Y.Z --certificate-identity-regexp ... --certificate-oidc-issuer https://token.actions.githubusercontent.com`.
- E2E tests run on tags only (Playwright in CI).

---

## Reproducibility

`misinfo.repro` provides:

- `seed_everything(seed)` — seeds `random`, `numpy`, `PYTHONHASHSEED`.
- `hash_file(path)` / `hash_dir(path)` — sha256 fingerprints for data/model artifacts.
- `git_sha()` — current commit, for run metadata.

Bit-identical reruns are guaranteed only for `MISINFO_RETRIEVER=bm25` with a
pinned corpus and `llama_cpp` local inference. Web retrieval and remote LLMs
are non-deterministic by nature; see [docs/MODEL-CARD.md](docs/MODEL-CARD.md)
for the full carve-out.

---

## Documentation map

### For users / operators
- [docs/OPERATOR-GUIDE.md](docs/OPERATOR-GUIDE.md) — running the service, env vars, troubleshooting.
- [docs/MODEL-CARD.md](docs/MODEL-CARD.md) — intended use, training data, calibration scope, known failure modes.
- [docs/EVALUATION-REPORT.md](docs/EVALUATION-REPORT.md) — Phase 7 numbers on AVeriTeC.
- [docs/LIMITATIONS.md](docs/LIMITATIONS.md) — what this system is **not** suitable for.

### For developers
- [docs/PROJECT-REPORT.md](docs/PROJECT-REPORT.md) — full project narrative across all phases.
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) — system diagram + module breakdown.
- [docs/api.md](docs/api.md) — API contract (also at `/openapi.json` when running).
- [docs/adr/](docs/adr/) — 19 architecture decision records.
- [docs/phase-2/SUCCESS-CRITERIA.md](docs/phase-2/SUCCESS-CRITERIA.md) — requirement traceability matrix.
- [docs/phase-11-security-review.md](docs/phase-11-security-review.md) — threat model + review.

---

## Project layout

```
.
├── docs/                Phase plans, ADRs, evaluation, model card, operator guide
├── data/                raw / interim / processed / external (gitignored when sensitive)
├── frontend/            Next.js 15 dashboard (verify + operator)
├── reports/             Generated evaluation reports
├── scripts/             Corpus builders, perf benchmarks, helpers
├── src/misinfo/         Importable package
│   ├── config.py        Settings
│   ├── decompose/       Sub-question generation
│   ├── retrieve/        Web (Tavily) + BM25 retrievers
│   ├── verify/          Aggregation, calibration, prompt safety
│   ├── services/        FastAPI app, auth, second-opinion sidecar
│   └── pipeline/        Orchestration + prompts
├── tests/               Pytest suite
├── .github/workflows/   CI, E2E, release
├── docker-compose.yml   Full stack (app + frontend + langfuse + prom + grafana)
├── Dockerfile           Backend image (multi-stage, non-root)
├── frontend/Dockerfile  Frontend image
├── pyproject.toml       Build + deps + tool config
├── environment.yml      Conda env
└── Makefile             dev / test / perf / docker shortcuts
```

---

## License & attribution

- Course project; see repository LICENSE for terms.
- Verdicts shown alongside Google Fact Check Tools results are © their respective publishers (Snopes, AFP, USA Today, etc.); we display them via the public Fact Check Tools API and link back to the originals.
- Web search powered by [Tavily](https://tavily.com).
- LLM inference via [Groq](https://groq.com).
- Trace export via [Langfuse](https://langfuse.com).
