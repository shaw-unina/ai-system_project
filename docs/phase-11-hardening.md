# Phase 11 — Hardening & Release

Phase 11 turned a feature-complete v0.x into a deploy-safe v1.0.0. No new
ML, no new endpoints beyond auth, no schema changes to `VerifyResponse`.

## Deliverables

| Bucket | What shipped |
|---|---|
| **Service auth** | Bearer-token auth + per-key sliding-window rate limit on `/v1/verify` and `/v1/batch`. Optional metrics token on `/metrics`. Auth no-ops when `MISINFO_API_KEYS` is empty. |
| **LLM-path safety** | `verify/safety.py` sanitizes user content (NFKC, strips controls + zero-width, neutralises fence escape) and wraps it in `<<<USER_CLAIM>>> … <<<END_USER_CLAIM>>>`. Prompt templates updated to instruct the model to treat the fence as data. |
| **Dashboard hardening** | Next middleware sets CSP / X-Frame-Options / X-Content-Type-Options / Permissions-Policy / Referrer-Policy on every response. `/operator` is cookie-gated by a single shared `OPERATOR_PASSWORD`. `/verify` stays open as the demo surface. |
| **Backend-key proxy** | Frontend reads `BACKEND_API_KEY` and `BACKEND_METRICS_TOKEN` server-side and injects them on the proxy hop; the browser never sees them. |
| **Container hardening** | Frontend Dockerfile now drops to a non-root `app` user. Backend Dockerfile already non-root. |
| **CI gates** | `pip-audit`, `npm audit --omit=dev`, `gitleaks`, OpenAPI→TS drift check (advisory until the committed types are wired). |
| **E2E** | Playwright config + two specs (verify flow, operator dashboard). Workflow runs on tags + manual dispatch only — PR cycles stay unit-only. |
| **Release pipeline** | `release.yml` builds both images on tag, pushes to GHCR with `vX.Y.Z` and `sha-<short>` tags, generates SPDX SBOMs via syft, signs images with cosign keyless, attaches SBOMs to the GitHub Release. |
| **Performance** | `scripts/perf_bench.py` for latency / throughput / memory; reports land in `reports/phase-11/` at release time. |
| **Final docs** | `MODEL-CARD.md`, `EVALUATION-REPORT.md`, `OPERATOR-GUIDE.md`, `ARCHITECTURE.md`, `LIMITATIONS.md`. |

## NFR closure

| NFR | Closed by |
|---|---|
| NFR-Lat-1 / NFR-Tput | `reports/phase-11/perf-*.md` (generated at release). |
| NFR-Trans-1 | MODEL-CARD + LIMITATIONS + EVALUATION-REPORT. |
| NFR-Trans-2 | Already implemented in Phase 8/10; smoke pending real-run. |
| NFR-Priv-1 | Auth + opt-in low-conf persistence + secret scan. |
| NFR-Maint-1/2 | pip-audit + npm audit advisory; lint/typecheck unchanged. |

## Verification

1. Backend: `pytest` — new `test_auth.py` (8 cases), `test_prompt_safety.py`
   (5 cases) plus existing 130 cases.
2. Frontend: `cd frontend && npm run lint && npm run typecheck && npm run
   test -- --run && npm run build` — all green.
3. Auth smoke: `curl -X POST localhost:8000/v1/verify -d '{"claim":"x"}'`
   returns 401 when `MISINFO_API_KEYS` set; 200 with the bearer header.
4. Rate-limit smoke: 70 requests/min with the default `60`/min limit
   produces ≥ 10 × 429.
5. E2E: `gh workflow run e2e.yml` against a Compose stack — three flows pass.
6. Perf: `make perf-latency` and `make perf-throughput` reports land in
   `reports/phase-11/`.
7. Tag + release: `git tag v1.0.0 && git push --tags` triggers
   `release.yml`; GHCR images, signatures, SBOMs published.

## Out of scope (post-1.0)

- Real SSO (OIDC, SAML).
- Per-user quotas with a real user model.
- Distributed tracing across services beyond Langfuse.
- K8s manifests / Helm chart.
- Managed-cloud deploys.
- Model retraining.
