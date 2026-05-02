# Phase 3 — Data Strategy: Decisions

ADR-style note. Captures choices made during Phase 3 implementation.

## Decisions

- **Primary benchmark:** AVeriTeC v2 (CC-BY-SA-4.0). Sourced from the FEVER 2025 task page; HF mirrors `chenxwh/AVeriTeC` and `pminervini/averitec`.
- **Secondary slice:** FakeNewsNet **PolitiFact text-only** (titles + URLs). Demoted from "secondary benchmark" to "drift / cross-domain slice" because tweet rehydration is no longer practical post-Twitter-API closure.
- **Attack set:** generated locally under `attack-set@v0` from AVeriTeC v2 fake claims, three styles (`newswire`, `tabloid`, `social`).
- **Splits:** `train`, `dev`, `test` as released by AVeriTeC; `dev_drift` derived as latest 20% by `claim_date`. Test split is locked at Phase 3 close — no peeking, no prompt iteration.
- **Versioning:** manifest-only (sha256 in `data/manifest.json`). DVC deferred until cross-machine sharing actually requires it.
- **Quality gates** for the attack pipeline: NLI ≥ 0.70 entailment, near-duplicate (token-Jaccard) < 0.85, length ratio in [0.5, 2.0]. Failures dropped, not scored.
- **Preprocessing:** NFC unicode + whitespace collapse + ≤ 4 000 character clip; idempotent; version `1`.
- **Test policy:** unit tests use synthetic fixtures only. Real-data downloads run locally on demand, never in CI.

## Explicitly deferred

- DVC / remote artefact storage.
- Real LLM paraphraser integration (Phase 6 wires a concrete model into `paraphrase.py`).
- Real NLI predictor integration (Phase 5/6 wires DeBERTa-v3-MNLI into `check_quality_gates`).
- CLI commands (`misinfo data download / prepare / attack-set / verify`) — Phase 5 will land them when there's an actual download path; for now the Python API is the contract.
- HuggingFace `datasets` and `huggingface_hub` deps — added when Phase 5 implements `download averitec`.

## Verification

- `pytest -q` passes (16 new tests across registry / preprocessing / splits / manifest / attack pipeline).
- All Phase 0 tests still pass.
- Cross-references to Phases 0/1/2 verified manually.
