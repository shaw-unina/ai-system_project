# Scope

**Status:** DRAFT
**Locks:** the input modality, output contract, language coverage, latency budget, and hardware target. Everything below is fixed for Phases 3–11 unless an explicit amendment is recorded here.

## Locked dimensions

| Dimension | Decision | Rationale |
|---|---|---|
| Input modality | **Text only** (claims, news paragraphs, short posts) | Phase 1 deferred multimodal; image+text plumbing roughly doubles engineering load. |
| Language | **English only** for the controlled experiment | AVeriTeC v2 is English; multilingual evaluation requires CheckThat!-class infrastructure we don't have. |
| Maximum input length | 4,000 characters per claim/article | Matches AVeriTeC distribution and typical RAG context budgets at 7–8 B verifier scale. |
| Output contract | Structured object (see below) | Allows downstream UI / batch / API to share one schema. |
| Latency budget | **p50 ≤ 30 s, p95 ≤ 60 s** end-to-end per claim | p95 matches AVeriTeC-2 shared-task constraint (P07). |
| Hardware target | **Single GPU ≤ 24 GB VRAM** (consumer / Colab Pro); CPU fallback acceptable for offline runs | Matches AVeriTeC-2 reproducibility envelope; ensures professor and graders can run it. |
| Operating modes | (a) on-demand single-claim, (b) offline batch CSV | Streaming, real-time feeds, and online learning are out. |

## Output contract

```
Verdict {
  verdict:    one of {Supported, Refuted, NotEnoughEvidence, Abstain}
  confidence: float in [0, 1]                 # calibrated; produced by abstention head
  evidence:   list of EvidenceRef             # zero or more
  rationale:  string                          # natural-language justification
  metadata:   { model_version, config_hash, dataset_hash, generated_at_utc }
}

EvidenceRef {
  source_id:  string                          # dataset-defined identifier
  url:        string | null
  span:       string                          # quoted text used as evidence
  score:      float                           # retrieval / NLI alignment score
}
```

Two distinctions worth keeping straight:

- **`NotEnoughEvidence`** is a verdict *about the claim*: the corpus does not contain sufficient material to decide.
- **`Abstain`** is a system *action*: the model declines to issue a verdict because its own confidence is below the threshold τ. It is driven by the abstention head and can fire even when retrieved evidence is rich.

Both routes ship in the artefact. Phase 7's selective-prediction analysis is over `Abstain`; H1.d's null guard bounds the `Abstain` rate.

## Explicitly out of scope

- Image / video / audio inputs.
- Languages other than English (MuMiN small remains a Phase 7 stretch slice, not a primary measurement).
- Real-time / streaming verification.
- User accounts, persistent claim history, social-graph signals.
- Online learning or model updates from user feedback.
- Cloud deployment beyond what `docker compose up` can run on one machine.

## Amendments

*(none yet — append below if scope is changed, with date and author)*
