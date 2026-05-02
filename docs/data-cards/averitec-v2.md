# Dataset card — AVeriTeC v2

**Status:** DRAFT
**Registry key:** `averitec@v2`
**License:** CC-BY-SA-4.0
**Homepage:** https://fever.ai/2025/task.html
**Hugging Face mirrors:** `chenxwh/AVeriTeC`, `pminervini/averitec`

## Motivation

AVeriTeC is the canonical real-world claim-verification benchmark for the FEVER 2024 / 2025 shared tasks. It pairs natural-language claims drawn from public fact-checks with web-evidence question/answer pairs and a final verdict. Schlichtkrull et al. (2024) introduced it specifically to move past Wikipedia-only synthetic benchmarks (FEVER) toward open-web evidence retrieval.

We use it as the **primary in-distribution benchmark** for Phases 5–7.

## Composition

- 4,568 real-world claims fact-checked by 50 organisations.
- Each claim carries: claim text, claim date, fact-checker tags/topic labels, a set of question/answer pairs with cited evidence URLs, and a 4-way verdict label (`Supported`, `Refuted`, `Not Enough Evidence`, `Conflicting Evidence/Cherrypicking`).
- v2 (FEVER 2025) adds a revised document collection plus a more recent claim portion that we adopt as the **drift slice**.

## Collection process

Claims were sourced from public fact-check reports; evidence Q/A pairs were created by trained annotators searching the open web. Detailed methodology is in the AVeriTeC paper.

## Preprocessing we apply

- NFC unicode normalisation, internal whitespace collapse, ≤4 000 character clip on `claim` text (`misinfo.data.preprocessing`).
- All other fields preserved verbatim.

## Splits

- `train`, `dev`, `test` as released. We also derive a `dev_drift` slice from the most recent 20% of `dev` by `claim_date` (when not already labelled).

## Intended uses

- Single-claim verification accuracy (Phase 5/7).
- Calibration and selective-prediction analysis (Phase 7).
- Source pool for the LLM-paraphrase attack set (Phase 6).

## Out-of-scope uses

- Authoritative truth labelling — verdicts reflect evidence available at the time of fact-checking and to that fact-checker.
- Per-individual reputational claims.

## Known biases / limitations

- **English only.** Multilingual analysis is out of scope.
- **Topic skew:** US politics and public-health claims are over-represented.
- **Fact-checker-organisation bias:** verdicts inherit each organisation's editorial taxonomy.
- **Temporal coverage:** evidence URLs may rot; the bundled document collection partially mitigates this.
- **Verdict-class imbalance:** `Refuted` dominates; metric reporting must use macro-F1.

## Distribution

- Source-of-truth: FEVER 2025 task page; mirrors on Hugging Face.
- We do **not** redistribute raw AVeriTeC data in this repository. Users download it via `misinfo data download averitec --version v2`. License obligations follow CC-BY-SA-4.0.

## Maintenance

- Dataset hash is committed to `data/manifest.json` per Phase 3.
- Card updated when the source releases a new version or when we change preprocessing.
