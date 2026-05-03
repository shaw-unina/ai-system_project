# Success Criteria

**Status:** DRAFT
**Reads:** [REQUIREMENTS.md](REQUIREMENTS.md), [HYPOTHESES.md](HYPOTHESES.md)
**Read by:** Phase 7 (verification), Phase 11 (release sign-off)

The single source of truth for whether the project succeeded. Each row is a contract; each cell points to the artefact that proves it.

## Top-line criteria

The project succeeds iff all three of the following hold:

1. **System.** A Dockerised service satisfies FR-1 … FR-8 and NFR-Lat-1 / NFR-Tput on the target hardware.
2. **Research.** The H1 evaluation runs cleanly and either supports H1 with statistical significance or rejects it with documented threats-to-validity.
3. **Reproducibility.** Anyone can clone the repo, run `docker compose up`, reproduce the headline metrics in the final report within tolerance, and inspect the model + dataset + ethics cards.

If any one of the three fails, the project ships partially and the report records the gap.

## Traceability matrix

| ID | Class | Verified in | Artefact path (when produced) |
|---|---|---|---|
| FR-1 | Functional | Phase 5 / 8 | `src/misinfo/inference.py`, `tests/test_verify_contract.py` |
| FR-2 | Functional | Phase 5 | `src/misinfo/schemas.py`, schema test |
| FR-3 | Functional | Phase 6 / 7 | `src/misinfo/abstention.py`, ablation in `reports/h1b.md` |
| FR-4 | Functional | Phase 5 / 7 | `src/misinfo/cli.py batch`, `tests/test_batch_cli.py` |
| FR-5 | Functional | Phase 8 | `src/misinfo/services/api.py`, `tests/test_api_contract.py` |
| FR-6 | Functional | Phase 5 | `Verdict.metadata` in schema test; `reports/run-manifest.json` |
| FR-7 | Functional | Phase 7 | `src/misinfo/cli.py audit`, `reports/adversarial-audit.md` |
| FR-8 | Functional | Phase 6 / 8 | `src/misinfo/abstention.py` rationale builder |
| NFR-Acc-1 | Accuracy | Phase 5 / 7 | `reports/baseline-eval.md` |
| NFR-Acc-2 | Accuracy | Phase 7 | `reports/h1a.md`, `reports/h1b.md` |
| NFR-Acc-3 | Accuracy | Phase 7 | `reports/averitec-score.md` |
| NFR-Cal-1 | Calibration | Phase 7 | `reports/calibration.md` |
| NFR-Cal-2 | Calibration | Phase 7 | `reports/risk-coverage.md` |
| NFR-Cal-3 | Calibration | Phase 7 | same |
| NFR-Rob-1 | Robustness | Phase 7 | `reports/robustness.md` |
| NFR-Rob-2 | Robustness | Phase 7 | `reports/error-decomposition.md` |
| NFR-Lat-1 | Latency | Phase 8 / 11 | `reports/phase-11/perf-latency.md` (release-time) |
| NFR-Tput | Throughput | Phase 8 / 11 | `reports/phase-11/perf-throughput.md` (release-time) |
| NFR-Expl-1 | Explainability | Phase 5 | `tests/test_verify_contract.py` |
| NFR-Trans-1 | Transparency | Phase 9 / 11 | [docs/MODEL-CARD.md](../MODEL-CARD.md), [docs/data-cards/](../data-cards/), [docs/LIMITATIONS.md](../LIMITATIONS.md) — shipped |
| NFR-Trans-2 | Transparency | Phase 8 / 10 | API spec, dashboard banner — implemented (smoke pending real-run) |
| NFR-Fair-1 | Fairness | Phase 7 | `reports/fairness.md` |
| NFR-Fair-2 | Fairness | Phase 7 | same |
| NFR-Repro-1 | Reproducibility | Phase 0 / 5 | re-run check in `tests/test_determinism.py` |
| NFR-Repro-2 | Reproducibility | Phase 5 | `tests/test_repro.py` (already exists) |
| NFR-Priv-1 | Privacy | Phase 8 / 11 | API/log review + [phase-11-security-review.md](../phase-11-security-review.md) — shipped |
| NFR-Priv-2 | Privacy | Phase 3 | dataset cards |
| NFR-Maint-1 | Maintainability | Phase 5+ | coverage report in CI |
| NFR-Maint-2 | Maintainability | Phase 0+ | already enforced |
| H1.a | Hypothesis | Phase 7 | `reports/h1a.md` |
| H1.b | Hypothesis | Phase 7 | `reports/h1b.md` |
| H1.c | Hypothesis | Phase 7 | `reports/h1c.md` |
| H1.d | Hypothesis | Phase 7 | `reports/h1d.md` |

Artefact paths are *target paths*; they don't all exist yet. They get created as their owning phase produces them.

## Tolerances for "reproduce within tolerance"

When a third party re-runs the eval harness on the target hardware, the headline numbers should agree within:

- F1, accuracy: ± 0.5 abs pts (dominated by GPU non-determinism in attention kernels).
- ECE, AURC: ± 0.01.
- Latency: ± 20% (hardware-dependent).
- Bootstrap CIs: same conclusion (supported / rejected) at 95%.

Bit-identical reproducibility (NFR-Repro-1) holds **only** when the same hardware + library versions are used; the looser tolerance above is the cross-machine contract.
