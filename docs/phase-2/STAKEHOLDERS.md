# Stakeholders & Use Cases

**Status:** DRAFT

## Personas

### S1 — Journalist / fact-checker (primary)

**Goal.** Decide quickly whether a circulating claim is supported, refuted, or undecidable.

**What they care about.**
- Verdict + supporting evidence + a short rationale, in under a minute.
- Trustworthy uncertainty: when the system is unsure, it must *say so* rather than emit a confident wrong answer (per P05, PNAS 2024 — confident wrong fact-checks reduce user accuracy on true headlines).
- Provenance: the evidence references must point to real, retrievable sources.

**What would make this useless.**
- Hallucinated citations.
- Confidence scores that don't track accuracy.
- Black-box verdicts with no rationale.

### S2 — Platform trust-and-safety analyst (secondary)

**Goal.** Triage thousands of claims per day; prioritise human review time.

**What they care about.**
- Throughput (≥ 10 claims/min, batched).
- Slice metrics — false positives by topic, source type, time window.
- A defensible abstention rate; routing high-uncertainty claims to humans.

**What would make this useless.**
- Per-claim latency dominating batch time.
- Drift on emerging topics with no signal that the model is out of distribution.

### S3 — Researcher / project team (tertiary)

**Goal.** Run controlled experiments that are reproducible from a commit + config + data hash.

**What they care about.**
- Deterministic eval harness.
- Hashed dataset/model artefacts (Phase 0 `misinfo.repro`).
- Tracked runs comparable across seeds and ablations.

**What would make this useless.**
- Non-deterministic baselines.
- Metrics that disagree between local and CI runs.

## Use cases

### UC-1 — Single-claim verification (S1)

```
Actor:        Journalist
Trigger:      Pastes a claim into the dashboard or hits the /verify HTTP endpoint
Pre:          Service is running; model loaded
Steps:
  1. Submit claim (≤ 4 000 chars, English)
  2. System retrieves evidence, runs verifier, computes confidence
  3. System returns a Verdict object
Post:         Journalist sees verdict, confidence, evidence list, and rationale
SLO:          p95 latency ≤ 60 s
Failure mode: confidence < τ → verdict = Abstain, rationale explains why
```

### UC-2 — Batch evaluation on a custom CSV (S2)

```
Actor:        Trust-and-safety analyst
Trigger:      Uploads a CSV of claims (one column "claim", optional "id")
Pre:          Service is running
Steps:
  1. CSV is processed row by row, preserving order
  2. Each claim is verified
  3. Results CSV emitted with columns: id, claim, verdict, confidence, evidence_ids, rationale, latency_ms
Post:         Analyst gets a CSV they can pivot in Excel / pandas
SLO:          ≥ 10 claims / minute on the target hardware
```

### UC-3 — Adversarial robustness audit (S3)

```
Actor:        Researcher
Trigger:      Runs the LLM-paraphrase attack set against a candidate model
Pre:          Attack set generated; model versioned
Steps:
  1. Researcher selects a claim subset and one or more attack styles
  2. Attack set runs through the verifier with abstention enabled and disabled
  3. Eval harness produces F1, ECE, AURC, accuracy@coverage tables per attack family
Post:         Markdown report under reports/ with metric tables, reliability diagrams,
              risk-coverage curves, and per-style examples of flipped verdicts
SLO:          Determinism: same commit + config + data hash → bit-identical metrics
```

These three use cases drive the FR list in [REQUIREMENTS.md](REQUIREMENTS.md).
