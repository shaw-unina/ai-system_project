# Ethics & Responsible Use

**Status:** DRAFT
**Reads:** [SCOPE.md](SCOPE.md), [REQUIREMENTS.md](REQUIREMENTS.md)
**Read by:** Phase 11 (release), and any time the team makes a public-release decision

This is a one-page note, not a treatise. The point is to make the dual-use posture and release decisions explicit so they aren't relitigated mid-Phase-7.

## Framing

The system is an **evidence-providing assistant**, not an oracle. Every output ships with evidence references and a rationale. The verdict label is one signal among several; the evidence is the part the user is meant to act on.

This framing matters because the PNAS 2024 study (P05 in [literature-matrix.csv](../phase-1/literature-matrix.csv)) showed that confident-wrong fact-check verdicts measurably *reduce* user accuracy on true headlines. The abstention head (FR-3) and the always-attached evidence (NFR-Expl-1) exist to keep the system from being read as authoritative when it is unsure.

## Dual-use considerations

The Phase 6 attack-set generator (the "Virtual Hacker" companion in the course PDF) is dual-use: the same paraphrasing pipeline that stress-tests the detector can also generate plausible misinformation at scale.

**What we will release:**
- Source code for the detector and the paraphraser.
- Configuration files, including the prompts used to generate paraphrases.
- A small, illustrative attack-set sample (≤ 50 examples) to support reviewers reproducing headline figures.

**What we will not release:**
- The full attack set as a downloadable corpus.
- Any pre-computed paraphrases that target specific real-world claims (we paraphrase only AVeriTeC v2 verified-fake claims for the controlled experiment).
- Fine-tuned weights of the paraphraser if those weights would meaningfully reduce the cost of generating misinformation at scale beyond a stock open-weight LLM.

The asymmetry is deliberate: making the *defence* reproducible is the project's value; making the *attack* trivially reusable is not.

## Data handling

- All datasets used (AVeriTeC v2, FakeNewsNet, MuMiN small if used) are public benchmarks with published licences. Licences are recorded in dataset cards in Phase 3.
- We do not scrape live social media or private posts.
- The service does not persist user-submitted claims by default (NFR-Priv-1). When persistence is enabled for evaluation runs, the run manifest hashes the input rather than storing the raw text.

## Hosted inference (Groq)

Per ADR-0002, the default inference backend is **Groq** — a hosted inference provider running open-weight models (Llama-3.3-70B, Qwen-2.5-32B). This means **claim text leaves the local environment** for the duration of each `verify(...)` call.

- For the controlled experiment we send only public AVeriTeC v2 claims, which are already published by their fact-checkers. No new disclosure.
- For arbitrary user-submitted claims (UC-1), the API documentation and dashboard copy must surface this fact (NFR-Trans-2).
- Sensitive deployments switch to the optional `llama_cpp` backend (offline, slower).
- Trace data (prompts, responses, latencies, token counts) is captured by **Langfuse Cloud** at `https://cloud.langfuse.com` — this means trace data also leaves the box. The self-hosted Langfuse v2 stack remains available via `docker-compose.yml` as a fallback for sensitive deployments; switch by setting `LANGFUSE_HOST=http://langfuse-server:3000` (compose-internal) or `http://localhost:3000` (host).

## Truth-claim posture

The system labels claims as `Supported`, `Refuted`, `NotEnoughEvidence`, or `Abstain` *with respect to the available evidence corpus*. It does not label claims as "true" or "false" in the abstract. This distinction shows up in:

- The UI / API copy (NFR-Trans-2): verdicts are phrased as "Evidence supports / refutes / is insufficient for" the claim.
- The model card (NFR-Trans-1): the limitations section states the corpus dependence explicitly.
- The rationale (FR-2): always references the retrieved evidence.

## Misuse modes we accept residual risk for

- A user can ignore the abstention signal and treat low-confidence verdicts as authoritative. Mitigation: visual + textual disclosure (NFR-Trans-2).
- A motivated adversary can study the released code and craft attacks beyond the three families we evaluate. Mitigation: this is the cost of open science; we publish the failure analysis (NFR-Rob-2) so defenders see the same gap.
- The evidence corpus may contain biased or low-quality sources. Mitigation: dataset cards (Phase 3) document known biases; fairness slices (NFR-Fair-1/2) surface where verdicts skew by topic.

## Final check before release (Phase 11)

The release checklist will include:

- [ ] Model card present, including known failure modes and the AVeriTeC v2 dependence.
- [ ] Dataset cards for every dataset that ships with or is referenced by the repo.
- [ ] Limitations statement linked from README.
- [ ] Attack-set sample is ≤ 50 examples and labelled as such.
- [ ] No credentials, API keys, or PII committed.
- [ ] License of all third-party assets verified.

These map onto NFR-Trans-1, NFR-Priv-1/2, and NFR-Trans-2.
