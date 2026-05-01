# Probe — Angle 1: Robustness to LLM-generated misinformation

**Status:** PROVISIONAL — values below are *literature-grounded plausible estimates* extrapolated from P21 (SheepDog, KDD 2024) and P22 (Chen, ICLR 2024), not measurements. Replace with real numbers when the probe is run.
**Owner:** probe engineer (TBD)
**Wall-clock budget:** half a day on a single consumer GPU
**Related papers:** P21 (SheepDog), P22 (Chen ICLR 2024), P23 (Nature Comms 2025)

## Question

How much does a strong text-only baseline detector degrade when fed LLM-generated paraphrases of the same claims, holding the *truth label* constant?

## Why this question matters

P22 and P23 both report large detection gaps between human-written and LLM-written misinformation, and P21 (SheepDog, KDD 2024) measured a **38% F1 drop** for SOTA detectors under LLM-empowered style attacks. If we can reproduce a drop of similar magnitude on our chosen baseline + dataset, the angle is alive and worth committing 8 weeks to. If the drop is small (< 5 absolute points), the angle is weaker than the literature implies and we should fall back to angle 2 or 4.

## Setup

| Component | Choice | Rationale |
|---|---|---|
| Detector | `MoritzLaurer/DeBERTa-v3-large-mnli-fever-anli` (or RoBERTa-large fine-tuned on FakeNewsNet) | Strong open-weights baseline; fits on 1× consumer GPU |
| Source dataset | FakeNewsNet (PolitiFact split) **or** AVeriTeC v2 dev | Public, labelled, manageable size |
| Paraphraser LLM | Llama-3.1-8B-Instruct or Qwen2.5-7B-Instruct (4-bit) | Open-weight; fits in 16 GB VRAM |
| Eval set size | 200 claims, balanced by label | Enough for a decision; not enough for a paper |

## Procedure

1. Sample 200 labelled claims from the eval split (100 fake, 100 real).
2. **Original-fakes pass.** Run the detector on the unmodified claims. Record per-claim probabilities + verdicts.
3. **Generate LLM paraphrases.** For each fake claim, prompt the paraphraser with three styles: (a) news-wire neutral, (b) tabloid, (c) social-media-thread. Keep the propositional content; vary only style. Save with hashes (Phase 0 `misinfo.repro.hash_file`).
4. **Style-attack pass.** Run the detector on the paraphrases.
5. Report:
   - F1 (original) vs F1 (paraphrase) per style.
   - Confusion-matrix delta.
   - 10 examples where the detector flipped from "fake" to "real".

## What the literature predicts

- P21 expects 15–38% F1 drop for an unaugmented detector.
- P22 expects the drop to be larger for "tabloid" / sensational reframings than for "news-wire neutral".
- P23 expects detector confidence to *increase* on the wrong answer for some paraphrases — the worst possible failure for downstream users (echoes P05 PNAS).

## Decision rules from the probe

| Observed F1 drop | Verdict for angle 1 |
|---|---|
| ≥ 15 abs points | Angle 1 alive; primary candidate confirmed |
| 5–15 abs points | Marginal; only pursue if calibration probe (angle 4) also shows headroom |
| < 5 abs points | Drop the angle; reuse the LLM-paraphrase corpus as a robustness slice for whichever angle wins |

## Risks for this probe specifically

- **Paraphraser quality.** If Llama-3-8B paraphrases are obviously off-topic, F1 drop is confounded. Mitigation: spot-check 20 paraphrases for label preservation before scoring.
- **Cherry-picking the detector.** If the chosen detector is the one SheepDog already targeted, results are over-determined. Mitigation: also try a generic NLI-based zero-shot classifier as a second baseline.

## Results (plausible, literature-grounded)

| Detector | Slice | F1 | Macro-F1 | ECE | Notes |
|---|---|---|---|---|---|
| DeBERTa-v3-mnli | original-fakes | 0.78 | 0.77 | 0.09 | In-distribution baseline; matches typical FakeNewsNet/AVeriTeC numbers |
| DeBERTa-v3-mnli | paraphrase-newswire | 0.65 | 0.64 | 0.13 | ~13 pt drop; neutral style mostly preserves topical cues |
| DeBERTa-v3-mnli | paraphrase-tabloid | 0.48 | 0.46 | 0.21 | ~30 pt drop; in line with SheepDog's reported 38% F1 ceiling |
| DeBERTa-v3-mnli | paraphrase-social | 0.55 | 0.53 | 0.18 | ~23 pt drop; informal register most degrades NLI head |

**Implied verdict:** F1 drop ≥ 15 abs points on at least two of the three attack styles. Decision rule "≥ 15 abs points → angle alive" is met under these assumptions. Confidence on the wrong class also rises (ECE doubles), reproducing the P05 "confident wrong" pattern.
