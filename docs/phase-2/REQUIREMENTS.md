# Requirements Specification

**Status:** DRAFT
**Reads:** [SCOPE.md](SCOPE.md), [STAKEHOLDERS.md](STAKEHOLDERS.md)
**Read by:** Phases 3, 4, 5, 7, 8, 10, 11

Every requirement carries an **ID**, a **statement**, a **rationale**, a **verification phase**, and (for NFRs) a **metric + threshold**. IDs are immutable once `LOCKED`.

---

## Functional Requirements (FR)

| ID | Statement | Rationale | Verified in |
|---|---|---|---|
| **FR-1** | The system shall expose a single-claim verification function `verify(claim: str) -> Verdict`. | UC-1 | Phase 5 (unit) / 8 (HTTP) |
| **FR-2** | The `Verdict` object shall contain `verdict`, `confidence`, `evidence`, `rationale`, and `metadata` as defined in [SCOPE.md](SCOPE.md). | Schema lock | Phase 5 |
| **FR-3** | The system shall implement an abstention mechanism that emits `verdict = Abstain` when confidence is below a configurable threshold τ. | UC-1, H1 | Phase 6 / 7 |
| **FR-4** | The system shall accept a CSV batch input and emit a results CSV preserving row order, with one row per input claim. | UC-2 | Phase 5 (CLI) / 7 |
| **FR-5** | The system shall expose an HTTP endpoint matching the same `verify` contract. | UC-1, dashboard hand-off | Phase 8 |
| **FR-6** | Every run shall persist a deterministic hash of `(model_version, config, dataset_hash)` and emit it in `Verdict.metadata`. | NFR-Repro | Phase 5 |
| **FR-7** | The system shall ship an "adversarial audit" command that runs a configured attack set against a chosen model and produces per-style metric tables. | UC-3 | Phase 7 |
| **FR-8** | When `verdict = Abstain`, the rationale shall state *why* (low confidence, insufficient evidence, retrieval-quality flag, or combination). | NFR-Trans-2 | Phase 6 / 8 |

---

## Non-Functional Requirements (NFR)

NFRs are organised by quality attribute. Each row is one testable contract.

### Accuracy

| ID | Metric | Threshold | Verified in |
|---|---|---|---|
| **NFR-Acc-1** | Macro-F1 on AVeriTeC v2 dev (clean) | ≥ reproducible baseline (Phase 5) | Phase 5 / 7 |
| **NFR-Acc-2** | Macro-F1 drop under each LLM-paraphrase attack family, with abstention enabled | ≤ 10 abs points on each style | Phase 7 |
| **NFR-Acc-3** | AVeriTeC score (Ev2R recall) for benchmark comparability | Reported (no hard threshold) | Phase 7 |

### Calibration & selective prediction

| ID | Metric | Threshold | Verified in |
|---|---|---|---|
| **NFR-Cal-1** | ECE on AVeriTeC v2 dev | ≤ 0.10 | Phase 7 |
| **NFR-Cal-2** | Accuracy at coverage 0.7 | ≥ full-coverage accuracy + 5 abs pts | Phase 7 |
| **NFR-Cal-3** | AURC (area under risk–coverage) | Reported with bootstrap CI | Phase 7 |

### Robustness

| ID | Metric | Threshold | Verified in |
|---|---|---|---|
| **NFR-Rob-1** | Per-style F1 on three LLM-paraphrase families (newswire / tabloid / social) | All three measured and reported | Phase 7 |
| **NFR-Rob-2** | Retrieval-failure share of high-confidence wrong verdicts | Reported (informs abstention) | Phase 7 |

### Latency & throughput

| ID | Metric | Threshold | Verified in |
|---|---|---|---|
| **NFR-Lat-1** | End-to-end latency per claim (p50 / p95) | ≤ 30 s / ≤ 60 s | Phase 8 |
| **NFR-Tput** | Sustained batch throughput | ≥ 10 claims / minute | Phase 8 |

### Explainability & transparency

| ID | Metric | Threshold | Verified in |
|---|---|---|---|
| **NFR-Expl-1** | Verdicts carrying at least one evidence reference and a rationale | 100% of non-`Abstain` outputs | Phase 5 |
| **NFR-Trans-1** | Model card + dataset card + limitations statement | Present at release | Phase 9 / 11 |
| **NFR-Trans-2** | UI/API responses identify the system as AI-generated and flag low-confidence outputs | Implementation review pass | Phase 8 / 10 |

NFR-Trans-1/2 are inspired by EU AI Act Article 13 (transparency to deployers) and Article 50 (transparency for AI-generated content). The system isn't legally in scope, but those checklists are the cleanest existing template for misinformation-flavoured AI.

### Fairness

| ID | Metric | Threshold | Verified in |
|---|---|---|---|
| **NFR-Fair-1** | Macro-F1 spread across AVeriTeC topical slices (politics, health, climate, …) | ≤ 10 abs points spread | Phase 7 |
| **NFR-Fair-2** | Abstention-rate spread across the same slices | ≤ 0.20 spread | Phase 7 |

### Reproducibility

| ID | Metric | Threshold | Verified in |
|---|---|---|---|
| **NFR-Repro-1** | Re-run with identical commit + config + data hash | Bit-identical metrics | Phase 0 / 5 |
| **NFR-Repro-2** | Random-seed control across all training/eval scripts | Asserted in tests | Phase 5 |

### Privacy & data handling

| ID | Metric | Threshold | Verified in |
|---|---|---|---|
| **NFR-Priv-1** | No PII persisted by default; logs redact claim text on opt-out flag | Implementation review | Phase 8 |
| **NFR-Priv-2** | Datasets used are public, with documented licences | Dataset cards check pass | Phase 3 |

### Maintainability

| ID | Metric | Threshold | Verified in |
|---|---|---|---|
| **NFR-Maint-1** | Unit test coverage on `src/misinfo/` | ≥ 60% | Phase 5+ |
| **NFR-Maint-2** | Lint + type checks pass on every change | Pass | Phase 0+ |

---

## Verification phase legend

- **Phase 0** — already shipped (foundations, repro primitives, lint/type/test).
- **Phase 3** — data strategy.
- **Phase 5** — baseline implementation & evaluation harness.
- **Phase 6** — proposed method.
- **Phase 7** — controlled evaluation.
- **Phase 8** — service layer & local deployment.
- **Phase 9** — monitoring & quality gates.
- **Phase 10** — frontend dashboard (next year).
- **Phase 11** — hardening & release.

A requirement that is not referenced by at least one downstream phase plan is a smell — review it.
