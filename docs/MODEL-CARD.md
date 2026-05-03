# Model Card — misinfo

**System:** retrieval-augmented LLM fact-checker, v1.0.0.
**Maintainer:** project authors (`README.md`).
**Released:** Phase 11 tag (`v1.0.0`).

## Intended use

Single-claim verification: given a short text claim, the system returns one of
`Supported` / `Refuted` / `NotEnoughEvidence` / `Abstain`, a confidence in
`[0, 1]`, an evidence list, and a free-form rationale. Designed for **human-
in-the-loop** review of news-style claims similar to AVeriTeC v2.

**Primary use case (UC-1, [the system scope](LIMITATIONS.md)):** an analyst submits a
claim and inspects the verdict + evidence + rationale before publishing.

## Out of scope

- Real-time / streaming social-media moderation.
- Adjudication of subjective, opinion, or future-tense claims.
- Languages other than English.
- Multimodal inputs (images, audio, video).
- Legal, medical, or safety-critical decisions made without human review.

## Architecture

Claim → decompose into sub-questions → retrieve evidence (BM25 + dense
hybrid) → answer each sub-question with the LLM → aggregate into a verdict
with calibrated confidence. Abstention is gated on a calibrated threshold τ
plus a retrieval-quality flag (Phase 6). Full diagram in
[ARCHITECTURE.md](ARCHITECTURE.md).

## Training data

The system itself is not trained — the LLM backend (`groq` default,
`llama_cpp` optional) is third-party. Calibration parameters τ and the
isotonic head were fit on AVeriTeC v2 dev. See
[DATASET-CARDS.md](data-cards/) for split, licence, and provenance.

## Calibration scope

The calibration / abstention numbers below were fit on AVeriTeC v2 with
BM25 retrieval over the gold corpus. They apply **only** when the system
is run as `MISINFO_RETRIEVER=bm25 MISINFO_CORPUS_PROFILE=averitec`. The
default deploy (`MISINFO_RETRIEVER=web`) still emits confidence scores
but they are *not* calibrated against the metrics in this card. See
[ADR-0017](adr/0017-web-retriever-default.md).

## Evaluation

| Metric | Slice | Result | Source |
|---|---|---|---|
| Macro-F1 | AVeriTeC v2 dev (clean) | ≥ Phase 5 baseline | [reports/phase7/results.md](../reports/phase7/) |
| Macro-F1 | LLM-paraphrase (3 styles) | drop ≤ 10 abs pts | same |
| ECE | dev | ≤ 0.10 | same |
| Accuracy @ coverage 0.7 | dev | ≥ full + 5 pts | same |
| Topical-slice F1 spread | dev | ≤ 10 abs pts | same |

See [EVALUATION-REPORT.md](EVALUATION-REPORT.md) for the full narrative.

## Known failure modes

1. **Retrieval misses.** If no evidence index covers the claim's domain, the
   verifier is forced to guess from the LLM's parametric knowledge.
   Mitigation: abstention head flags low retrieval quality → `Abstain`.
2. **LLM-paraphrased fakes.** Tabloid-style paraphrase shifts F1 the most;
   reported per-style in Phase 7.
3. **Stale knowledge.** The LLM's training cutoff is older than the evidence
   corpus. Recent claims (post-cutoff) lean on retrieval, not parametric
   recall.
4. **Prompt injection.** Phase 11 wraps user content in a labelled fence and
   maps refusals to `Abstain`; novel attacks may still slip through.

## Fairness

Per-slice F1 spread on AVeriTeC topical slices (politics, health, climate,
…) is bounded by NFR-Fair-1 (≤ 10 abs points). Abstention-rate spread
bounded by NFR-Fair-2 (≤ 0.20). Numbers in
[reports/phase7/fairness.md](../reports/phase7/).

## Privacy

`MISINFO_BACKEND=groq` (default) ships claim text to a third-party LLM
provider; document this for any deployment touching PII. The optional
`llama_cpp` backend keeps inference on-box. Logs redact claim text on the
opt-out flag (NFR-Priv-1). No claim text is persisted server-side by the
dashboard (Phase 10/11).

## Limitations

See [LIMITATIONS.md](LIMITATIONS.md).

## Versioning

`Verdict.metadata` carries `(backend, model_id, model_version, seed,
temperature, langfuse_trace_id)` (NFR-Repro-1). Reproducibility tolerances
in [phase-2/SUCCESS-CRITERIA.md](phase-2/SUCCESS-CRITERIA.md).
