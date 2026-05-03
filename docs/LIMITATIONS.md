# Limitations

This document is the canonical place users and operators should look to
understand what the misinfo system **does not do**.

## Claim scope

- **English only.** Cross-lingual retrieval and verification are out of
  scope for v1.0.
- **Short factual claims, not opinions.** Subjective, normative, or
  future-tense claims (`"X should be banned"`, `"Y will happen"`) are not
  supported and will frequently abstain.
- **News-style domain.** Calibration was fit on AVeriTeC; out-of-domain
  claims (scientific literature, legal text, medical advice) will degrade.

## Output semantics

- A `Supported` verdict with high confidence **does not mean the claim is
  true.** It means the retrieved evidence supports it. Sources can be
  wrong, biased, or stale.
- The rationale is a model-generated explanation, not a citation. Treat it
  as a starting point for review.
- Confidence scores are calibrated on a held-out dev set (ECE ≤ 0.10) and
  are best read as ordinal — a `0.83` claim is more likely correct than a
  `0.61` claim, but neither guarantees correctness.

## Operational

- **Third-party LLM.** Default backend (`groq`) routes claim text to an
  external service. Not appropriate for sensitive content without
  switching to `llama_cpp`.
- **Live web retrieval.** With `MISINFO_RETRIEVER=web` (default), claim
  text *and* sub-question rephrasings are sent to the search provider
  (Tavily). Set `MISINFO_RETRIEVER=bm25` for an air-gapped path that
  keeps queries on-box.
- **Second-opinion sidecar.** When `GOOGLE_FACT_CHECK_API_KEY` is set,
  the dashboard sends each claim to Google Fact Check Tools to surface
  third-party fact-check ratings. Disabled by default.
- **Calibration is corpus-bound.** The Phase 6 calibration (ECE ≤ 0.10,
  acc@coverage 0.7, AURC) was fit on AVeriTeC retrieval distributions.
  These numbers apply only to `MISINFO_RETRIEVER=bm25` with the
  `averitec` profile. With `web` retrieval, the system still emits
  confidences but they are no longer calibrated.
- **Reproducibility is retriever-bound.** Bit-identical reruns require
  `bm25` + `llama_cpp`. The `web` retriever is non-deterministic by
  construction (search index changes over time).
- **Latency variability.** p95 ≤ 60 s on the default backend assumes
  Groq's nominal latency; tail spikes on the provider side propagate
  through.
- **Evidence corpus is fixed at deploy time.** The system has no way to
  fetch new sources mid-request; the corpus must be re-indexed and
  redeployed for fresh evidence.

## Trust & safety

- **Not a content-moderation system.** Do not use for automated takedowns.
  The system is designed for human-in-the-loop review.
- **Prompt injection.** Phase 11 introduces fenced user content and
  refusal-to-abstain mapping, but novel attacks against the LLM remain
  possible.
- **Bias.** Topical-slice fairness is bounded but not eliminated. See
  [reports/phase7/fairness.md](../reports/phase7/).

## Known compromises

- The dashboard's low-confidence table is **session-local** (browser
  `localStorage`) by default. Server-side persistence is opt-in and
  per-API-key.
- Auth is **bearer-token only** (no users, no roles). The operator
  dashboard uses a single shared password.
- The release pipeline signs images via cosign keyless; verifying
  signatures requires the GitHub OIDC issuer to be trusted.
