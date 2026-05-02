# Phase 2 — Problem Definition & Requirements (artifacts)

This folder formalises what Phase 1 left as prose. It is the requirements specification that Phases 3 (data), 4 (architecture), 5 (baseline), 6 (proposed method), 7 (evaluation), 8 (service), 10 (dashboard), and 11 (release) build to and are graded against.

## Layout

```
phase-2/
├── README.md                this file
├── SCOPE.md                 locked scope: modality, language, output contract, latency, hardware
├── STAKEHOLDERS.md          personas + use cases (UC-1, UC-2, UC-3)
├── REQUIREMENTS.md          numbered FRs and NFRs with metrics, thresholds, and verification phases
├── HYPOTHESES.md            H1 (from Phase 1) + operational sub-hypotheses with statistical tests
├── SUCCESS-CRITERIA.md      ID → verification phase → artefact-path matrix
└── ETHICS.md                dual-use posture, release policy, truth-claim framing
```

## Status legend

- `DRAFT` — first pass; reviewable but expected to change.
- `REVIEWED` — internal review pass complete; one team member's objections recorded.
- `LOCKED` — frozen for Phase 3+. Changes require a documented amendment.

Every document in this folder carries one of these tags at the top.

## How to use this folder

- **Phase 3 (data)** reads `SCOPE.md` (modality + language) and `REQUIREMENTS.md` NFR-Acc / NFR-Fair to pick datasets and slices.
- **Phase 4 (architecture)** reads `REQUIREMENTS.md` FR-1…FR-6 + NFR-Lat / NFR-Tput / NFR-Expl to choose architecture.
- **Phase 5 (baseline)** reads `SUCCESS-CRITERIA.md` to scope the evaluation harness.
- **Phase 7 (evaluation)** reads `HYPOTHESES.md` and `SUCCESS-CRITERIA.md` end-to-end.
- **Phase 11 (release)** reads `REQUIREMENTS.md` NFR-Trans-1/2 + `ETHICS.md` to assemble model card + limitations statement.

## Cross-references upstream

- Project phase plan: [../phases.md](../phases.md)
- Phase 0 decisions: [../phase-0-foundations.md](../phase-0-foundations.md)
- Phase 1 decision: [../phase-1/DECISION.md](../phase-1/DECISION.md)
- Phase 1 hypothesis (H1) is restated verbatim inside [HYPOTHESES.md](HYPOTHESES.md).
