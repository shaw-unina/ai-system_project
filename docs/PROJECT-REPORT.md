# Misinformation Detector — Project Report

**Course:** AI Systems Engineering (Prof. Pietrantuono)
**Repository:** `nisha-shaw/project`
**Status:** Phases 0–11 complete; v1.0.0 released.

---

## 1. Executive summary

This project delivers a closed-book misinformation verification system that
takes a short factual claim, retrieves evidence from the live web (or a local
corpus), asks a large language model to score the evidence against
LLM-generated sub-questions, and returns a calibrated verdict —
**Supported**, **Refuted**, **Not enough evidence**, or **Abstain** — with a
rationale, the supporting evidence, and a confidence score the system is
willing to defend.

It was built as an end-to-end exercise in turning a research idea into a
deployable, observable, auditable service. The deliverable is not just a
model: it is a containerised stack (FastAPI backend, Next.js dashboard,
Langfuse traces, Prometheus + Grafana metrics), a test suite (22 backend +
18 frontend + tag-only Playwright), a CI/CD pipeline that signs releases
with cosign and ships SPDX SBOMs, and a documentation set (model card,
evaluation report, operator guide, architecture, limitations, and 19
ADRs).

The headline trade-off the project commits to is **calibrated abstention**:
the system would rather refuse to answer than be confidently wrong. That
trade-off is enforced everywhere — in the pipeline (Phase 6 abstention
head), in the UI (low-confidence flag, "AI-generated" disclosure popover,
"Other fact-checkers say" sidecar), and in the documentation (model card
caveats, limitations).

---

## 2. Motivation

LLMs hallucinate; misinformation classifiers overfit to surface features;
fact-check pipelines that look impressive on benchmarks fall over on the
open web. The interesting engineering question is not "can a model classify
claims?" — it is **"can a system know when not to answer, expose its
reasoning, and be trusted by an operator who has to act on its output?"**

That question is what shaped every phase. Where the easier choice would
have been to maximise headline accuracy, the project consistently chose to
maximise *defensible* accuracy — i.e., accuracy at a coverage level the
system itself selects.

---

## 3. Requirements & success criteria

Phase 2 froze a traceability matrix mapping each requirement to the phase
that verifies it and the artefact that proves it. A condensed view:

| Class           | Requirements                                                     | Verified in                |
|-----------------|------------------------------------------------------------------|----------------------------|
| **Functional**  | FR-1 … FR-8 (verify, batch, abstain with reasons, audit, schema) | Phases 5 / 6 / 7 / 8        |
| **Accuracy**    | NFR-Acc-1 (beat baseline), NFR-Acc-2 (paraphrase robustness)     | Phases 5 / 7                |
| **Calibration** | NFR-Cal-1 (ECE ≤ 0.10), NFR-Cal-2 (acc@coverage 0.7), NFR-Cal-3  | Phases 6 / 7                |
| **Robustness**  | NFR-Rob-1 (LLM paraphrase), NFR-Rob-2 (retrieval failure)        | Phase 7                     |
| **Performance** | NFR-Lat-1 (p50 ≤ 30 s, p95 ≤ 60 s), NFR-Tput (≥ 10 claims/min)   | Phases 8 / 11               |
| **Trans/Priv**  | NFR-Trans-1/-2 (model card, UI disclosure), NFR-Priv-1/-2        | Phases 8 / 9 / 10 / 11      |
| **Fairness**    | NFR-Fair-1/-2 (slice F1 spread, abstention spread)               | Phase 7                     |
| **Repro**       | NFR-Repro-1 (bit-identical), NFR-Repro-2 (re-run)                | Phase 0+ throughout         |
| **Maint**       | NFR-Maint-1 (coverage), NFR-Maint-2 (lint/type)                  | continuous                  |

Top-line gate: **succeed iff** (1) the Dockerised service satisfies the
functional + latency contract, (2) the H1 evaluation runs cleanly with
either statistical support or documented threats-to-validity, and (3) a
third party can clone the repo, `docker compose up`, and reproduce the
headline numbers within tolerance. All three hold at v1.0.0.

Full matrix in [phase-2/SUCCESS-CRITERIA.md](phase-2/SUCCESS-CRITERIA.md).

---

## 4. System architecture

### 4.1 Pipeline shape

```
claim ─▶ Decompose ─▶ Retrieve ─▶ Answer ─▶ Aggregate ─▶ Calibrated abstention
        (LLM)        (Web/BM25)  (LLM)     (LLM)        (verdict + confidence)
```

Each stage is a Protocol-typed module so that backends are swappable
without touching the orchestrator (ADR-0001). The orchestrator lives in
`src/misinfo/pipeline/` and reads its prompts from text files alongside the
code so they can be reviewed in PRs.

### 4.2 Component map

| Layer             | Tech                                       | Module / file                              |
|-------------------|--------------------------------------------|--------------------------------------------|
| Decompose         | Groq LLM (default)                         | `decompose/llm_decomposer.py`              |
| Retrieve (web)    | Tavily search API                          | `integrations/tavily.py`                   |
| Retrieve (local)  | Whoosh BM25 over JSONL corpus              | `retrieve/bm25_retriever.py`               |
| Answer            | Groq LLM, structured output                | `pipeline/answer.py`                       |
| Aggregate         | Groq LLM, JSON schema                      | `verify/aggregator.py`                     |
| Calibration       | Pluggable abstention head, τ-thresholding  | `verify/abstention.py`, models/calibration |
| Service           | FastAPI + uvicorn                          | `services/api.py`                          |
| Auth              | Bearer tokens + sliding-window limiter     | `services/auth.py`                         |
| Second opinion    | Google Fact Check Tools v1alpha1           | `services/second_opinion.py`               |
| Frontend          | Next.js 15 App Router, TanStack Query      | `frontend/`                                |
| Tracing           | Langfuse                                   | env-driven hooks                           |
| Metrics           | Prometheus client                          | `services/metrics.py`                      |

### 4.3 Decision records

19 ADRs document each load-bearing choice with the alternatives that were
considered and rejected. A few that mattered most:

- **ADR-0001** — Pipeline shape (decompose-retrieve-answer-aggregate vs. single-shot).
- **ADR-0003** — Verifier model (LLM with retrieval vs. fine-tuned encoder).
- **ADR-0007 / -0009** — Abstention interface and the heads behind it.
- **ADR-0010** — HTTP service framework (FastAPI vs. Flask vs. gRPC).
- **ADR-0013 / -0014** — Frontend stack and backend-proxy pattern.
- **ADR-0015 / -0016** — Bearer auth and operator password gate.
- **ADR-0017** — Web retrieval as default, BM25 as the calibrated path.
- **ADR-0018** — Second-opinion sidecar (display-only by design).
- **ADR-0019** — Design system (editorial minimalism + shadcn theming).

---

## 5. Phase-by-phase contributions

### Phase 0 — Foundations
Repository scaffolding on the `dev` branch, conda env, pinned deps,
formatter (black) + linter (ruff) + type checker (mypy) wired in CI from
day 1. Reproducibility primitives (`seed_everything`, `hash_file`,
`hash_dir`, `git_sha`) shipped before any model code, so every later
artefact carries a reproducible fingerprint.

### Phase 1 — Research scouting
Time-boxed survey of fact-checking literature 2023–2025: CheckThat!, FEVER,
AVeriTeC, plus selective-prediction and rationale-faithfulness work. The
output was a paper-tracking matrix and a decision document selecting
**calibrated abstention on retrieved evidence** as the angle, with
rejected alternatives recorded.

### Phase 2 — Problem definition
Scope locked to **English short factual claims**. Output contract specified
as a typed `VerifyResponse` (verdict + confidence + evidence + rationale +
metadata). Stakeholder model written down. The traceability matrix in §3
was produced here.

### Phase 3 — Data strategy
AVeriTeC v2 selected as the primary eval corpus (license-clean, claim-level
verdicts with evidence). Time-ordered splits to prevent temporal leakage.
Dataset cards written documenting source, biases, intended use. A separate
ingester for Wikipedia + a small smoke set built later in Phase 11.1.

### Phase 4 — System architecture
Three architecture options compared in writing — fine-tuned encoder,
retrieval-augmented LLM, hybrid. The hybrid won on ability to abstain
honestly, with the trade-off being latency. Module boundaries crystallised
into the pipeline shape in §4.1.

### Phase 5 — Baseline implementation
A strong reproducible baseline (fine-tuned encoder) built first, with the
full evaluation harness wired against it. Every later experiment is
measured against this reference.

### Phase 6 — Calibrated abstention (the research contribution)
The proposed method: a pluggable abstention head fit on a held-out dev set,
returning a calibrated probability. A τ-threshold rewrites low-confidence
verdicts to `Abstain` with the reasons exposed in the rationale. Iterated
against the harness until **ECE ≤ 0.10** and **acc@coverage 0.7 ≥ baseline
accuracy + 5 abs pts**.

### Phase 7 — Evaluation
Controlled comparison vs. the Phase 5 baseline across three seeds with
bootstrap CIs. Robustness suite: LLM paraphrase in three styles (newswire,
tabloid, social), retrieval-failure decomposition. Fairness slices across
topic clusters. Reliability diagrams + risk-coverage curves. Threats to
validity documented (provider drift, test-set contamination, paraphrase
coverage, annotator labels).

### Phase 8 — Service layer
FastAPI service exposing `/v1/verify`, `/v1/batch`, `/healthz`,
`/metrics`. Versioned schemas under `services/schemas.py`. Structured
logging with correlation IDs. Langfuse trace IDs threaded through into the
response metadata so any verdict can be traced back to its LLM calls.
Containerised; `docker compose up` brings the stack up.

### Phase 9 — Monitoring
Prometheus client with histograms for latency and counters for verdict
mix. Grafana dashboards provisioned in compose. Regression tests on a
frozen smoke set, gated by YAML-driven quality thresholds in CI.

### Phase 10 — Frontend dashboard
Greenfield Next.js 15 (App Router, TypeScript strict). Two surfaces:
`/verify` for end users, `/operator` for live metrics + report viewer +
recent low-confidence cases (held in browser session storage). React Query
for polling + mutations. TS types generated from the FastAPI OpenAPI to
keep the contract honest. The Next API routes proxy the backend so the
browser never sees the upstream URL.

### Phase 11 — Hardening & release
Bearer-token auth with comma-separated allowlist; per-key sliding-window
rate limiting. Prompt-injection mitigations (NFKC normalisation, control
character stripping, fenced user content). Cookie gate on `/operator`.
Security headers via Next middleware. Non-root Docker images. Advisory
`pip-audit` / `npm audit` / `gitleaks` in CI. OpenAPI→TS drift check
fails CI on schema changes that aren't regenerated. Tagged releases
publish cosign-signed images with SPDX SBOMs to GHCR. Final docs:
model card, evaluation report, operator guide, architecture, limitations.

### Phase 11.1 — Live retrieval + second-opinion sidecar
Made Tavily web retrieval the default so the system works on real-world
claims out of the box. Kept BM25 + AVeriTeC as the calibrated, reproducible
path. Added a `/v1/second-opinion` endpoint backed by Google Fact Check
Tools, with progressive query shortening (full → first sentence → first
8 words) to handle the API's keyword-match semantics. The sidecar is
**display-only**: results render next to the verdict for context but
never feed the verify pipeline.

### Phase 11.2 — Design system + dark mode
Editorial Minimalism for `/verify` (Newsreader display, Roboto UI, animated
SVG confidence dial, focus-trapped disclosure popover, evidence list with
show-more). Bento Dashboard for `/operator` (KPI tiles, sparkline, verdict
mix bar chart). Migrated to shadcn-style HSL CSS variable theming with
parallel `:root` (light) and `.dark` palettes; verdict tones tuned for
both modes. `next-themes` for system-default + manual toggle.

---

## 6. Evaluation results

Detailed tables and figures live in
[reports/phase7/](../reports/phase7/) and are summarised in
[EVALUATION-REPORT.md](EVALUATION-REPORT.md). The headline:

| Metric                          | Baseline | misinfo v1.0.0 | Status                |
|---------------------------------|----------|----------------|-----------------------|
| Macro-F1 (clean AVeriTeC dev)   | reference| ≥ baseline     | NFR-Acc-1 satisfied   |
| Macro-F1 drop, paraphrase suite | —        | ≤ 10 abs pts   | NFR-Acc-2 satisfied   |
| ECE                             | —        | ≤ 0.10         | NFR-Cal-1 satisfied   |
| Acc @ coverage 0.7              | —        | ≥ full + 5 pts | NFR-Cal-2 satisfied   |
| AURC (with 95% CI)              | —        | reported       | NFR-Cal-3 satisfied   |
| Topical-slice F1 spread         | —        | ≤ 10 abs pts   | NFR-Fair-1 satisfied  |
| Abstention-rate spread          | —        | ≤ 0.20         | NFR-Fair-2 satisfied  |
| p50 / p95 latency               | —        | ≤ 30 s / ≤ 60 s| NFR-Lat-1 satisfied   |
| Throughput                      | —        | ≥ 10 claims/min| NFR-Tput satisfied    |

Three seeds; mean ± 95 % bootstrap CI. The cross-machine reproduction
tolerance is documented in
[phase-2/SUCCESS-CRITERIA.md](phase-2/SUCCESS-CRITERIA.md): F1 ± 0.5 abs
pts, ECE ± 0.01, latency ± 20 %.

**Threats to validity** are recorded in EVALUATION-REPORT.md: provider
drift on Groq, AVeriTeC contamination in pre-training data, three
paraphrase styles do not exhaust the attack surface, and annotator label
noise inherited from AVeriTeC.

---

## 7. Engineering practices

### Testing
- **Backend** — 22 pytests covering decompose, retrieve, aggregate,
  abstention, the FastAPI contract, prompt safety, bearer auth + rate
  limiting, the second-opinion sidecar.
- **Frontend** — 18 vitests covering verdict card, confidence dial,
  disclosure popover, low-confidence session table, second-opinion card,
  and the metrics parser.
- **E2E** — Playwright suite that runs on tags only (CI tagged-only to
  keep PRs fast).
- **Type safety** — `tsc --noEmit` in CI; OpenAPI→TS drift check fails
  CI if the FastAPI schema changes without regenerating the TS types.

### CI/CD
GitHub Actions runs lint + typecheck + tests + build for both Python and
TypeScript on every PR. Advisory security passes (`pip-audit`, `npm audit`,
`gitleaks`) report findings without blocking. On a `vX.Y.Z` tag the
release workflow builds backend and frontend images, signs them with
cosign keyless via the GitHub OIDC issuer, attaches SPDX SBOMs produced
by syft, and publishes to GHCR.

### Security
Threat model and review: [phase-11-security-review.md](phase-11-security-review.md).
Highlights:
- Bearer-token auth with comma-separated allowlist; empty allowlist = unauthenticated (local dev only).
- Sliding-window rate limit per token (in-process, threading.Lock).
- `/metrics` token-gated separately so observability scrapers don't share the verify keys.
- `/operator` cookie-gated by `OPERATOR_PASSWORD`.
- Prompt safety: NFKC normalisation, control + zero-width stripping, fenced user content (`<<<USER_CLAIM>>>`).
- Non-root Docker users; security headers (CSP, HSTS, X-Frame-Options, X-Content-Type-Options, Referrer-Policy) via Next middleware.

### Observability
- **Langfuse** — every LLM call is traced; the trace ID is returned in `VerifyResponse.metadata` so any verdict can be opened in Langfuse.
- **Prometheus** — request counter (by verdict), latency histogram, abstention counter, retrieval-error counter.
- **Grafana** — dashboards provisioned in compose; verdict mix + p95 latency live tiles in the operator UI parse the same `/metrics` exposition.

---

## 8. Limitations

Captured in full in [LIMITATIONS.md](LIMITATIONS.md). The ones operators
must know:

1. **English short factual claims only.** Subjective, normative, or future-tense claims will frequently abstain.
2. **News-style domain.** Calibration was fit on AVeriTeC; out-of-domain claims (medical, legal, scientific) will degrade.
3. **A `Supported` verdict is not "true".** It means the *retrieved evidence* supports the claim. Sources can be wrong, biased, or stale.
4. **Calibration is corpus-bound.** Phase 6 calibration numbers apply only to `MISINFO_RETRIEVER=bm25` with the `averitec` profile. With `web` retrieval the system still emits confidences, but they are no longer guaranteed calibrated.
5. **Reproducibility is retriever-bound.** Bit-identical reruns require `bm25` + `llama_cpp`. The `web` retriever is non-deterministic by construction.
6. **Third-party LLM.** The default Groq backend routes claim text to an external service. For sensitive content, switch to `llama_cpp`.
7. **Not a content-moderation system.** Designed for human-in-the-loop review, not automated takedowns.

---

## 9. Reflection

### What worked
- **Phase plan up front.** Locking 11 phases with verifiable artefacts in Phase 2 made every subsequent decision easier. There were no "what should I build next" weeks.
- **Calibrated abstention as the research bet.** Abstain-rather-than-be-wrong is a cleaner user contract than chasing extra F1 points; it matched the trustworthiness theme of the course.
- **ADRs committed alongside code.** Future-me reading the repo can reconstruct *why* a choice was made, not just what was built.
- **Web retrieval as default, BM25 as the reproducible path.** The system actually works on arbitrary claims out of the box; reviewers can still reproduce the calibration story by flipping a single env var.
- **Documentation as a deliverable.** The model card, operator guide, evaluation report, and limitations are first-class artefacts, not afterthoughts.

### What was harder than expected
- **Google Fact Check Tools is keyword-matched.** Long natural claims returned empty. Solved with progressive query shortening, but the API's behaviour is not what its docs imply.
- **Prompt injection is unbounded.** The Phase 11 sanitisation closes the obvious holes (control chars, fence injection); novel attacks remain possible. This is an honest limitation, not a fix.
- **Calibration carve-outs.** Once web retrieval became the default, the Phase 6 calibration story had to be scoped to `bm25:averitec` explicitly. Honest, but annoying to communicate.
- **UI iteration.** The first dashboard pass looked like a generic AI demo. Two design-system iterations (editorial minimalism + dark mode) were needed before it felt trustworthy.

### What I would change
- **Add a SQL-backed low-confidence log.** The current session-localStorage approach is honest about its scope but limits operator usefulness across sessions.
- **Add Playwright e2e to PR CI, not just tag CI.** They were deferred to keep PRs fast; in hindsight a small smoke would have caught two regressions.
- **Adopt shadcn from day 1 of the frontend.** Building a custom component layer first and migrating was wasted motion.
- **Add a corpus-freshness widget.** The system has no way to fetch new sources mid-request, but the UI doesn't advertise this. A "corpus indexed YYYY-MM-DD" label would prevent confusion.

---

## 10. Future work

- **Multilingual.** v1.0 is English-only. The pipeline shape is
  language-agnostic; what's missing is multilingual retrieval + a calibrated
  abstention head per language.
- **Server-side persistence.** A small Postgres instance for low-confidence
  cases, per-API-key, would unlock cross-session operator workflows.
- **Streaming verdicts.** SSE the sub-question results as they complete; the
  current request blocks until aggregation, which feels sluggish at the p95.
- **Active learning loop.** Operators flagging false-positives via the
  dashboard could feed a relabeling queue.
- **Adversarial harness expansion.** Three paraphrase styles is a floor;
  prompt-injection-shaped attacks deserve their own evaluation.

---

## 11. Repository pointers

- **[README.md](../README.md)** — quickstart, configuration, doc map.
- **[docs/ARCHITECTURE.md](ARCHITECTURE.md)** — full system diagram + module breakdown.
- **[docs/MODEL-CARD.md](MODEL-CARD.md)** — intended use, training data, calibration scope, known failure modes.
- **[docs/EVALUATION-REPORT.md](EVALUATION-REPORT.md)** — Phase 7 numbers in full.
- **[docs/OPERATOR-GUIDE.md](OPERATOR-GUIDE.md)** — running the service, env vars, troubleshooting.
- **[docs/LIMITATIONS.md](LIMITATIONS.md)** — what the system is **not** suitable for.
- **[docs/api.md](api.md)** — API contract (also at `/openapi.json`).
- **[docs/adr/](adr/)** — 19 architecture decision records.
- **[docs/phases.md](phases.md)** — the phase plan that drove the project.
- **[docs/phase-2/SUCCESS-CRITERIA.md](phase-2/SUCCESS-CRITERIA.md)** — traceability matrix.
- **Per-phase notes** — `docs/phase-{0..11}-*.md`.

---

## 12. Acknowledgements

- Course staff and instructor (Prof. Pietrantuono) for the phase framework and trustworthiness focus.
- AVeriTeC v2 authors for the dev-set used in calibration and evaluation.
- Tavily, Groq, Langfuse, Google Fact Check Tools — third-party services consumed under their respective terms.
- Open-source dependencies: FastAPI, Pydantic, Whoosh, Next.js, TanStack Query, shadcn/ui, Recharts, Tailwind CSS, react-markdown, remark-gfm, lucide-react, next-themes.
