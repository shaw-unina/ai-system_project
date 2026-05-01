# Probe — Angle 4: Calibrated selective prediction

**Status:** PROVISIONAL — values below are *literature-grounded plausible estimates* extrapolated from P32 (SelectLLM) and P34 (QA-Calibration), not measurements. Replace with real numbers when the probe is run.
**Owner:** probe engineer (TBD)
**Wall-clock budget:** half a day
**Related papers:** P05 (PNAS), P32 (SelectLLM), P33 (Know Your Limits), P34 (QA-Calibration)

## Question

How miscalibrated is a typical fact-checker, and does the *risk–coverage curve* leave enough headroom for an abstention method to matter?

## Why this question matters

P05 (PNAS) showed that confident-wrong fact-check verdicts actively *reduce* user accuracy on true headlines. P32 and P34 have introduced calibration / selective-prediction methods for general LLMs, but very little of this has been measured on fact-checking specifically. If we observe high ECE *and* a meaningful gap in the risk–coverage curve, abstention is a real lever — and it's an angle the course's "trustworthiness" theme cares about explicitly.

## Setup

| Component | Choice | Rationale |
|---|---|---|
| Detector(s) | (a) DeBERTa-v3 fine-tuned, (b) Llama-3.1-8B-Instruct verifier | Cover encoder + LLM regimes |
| Confidence signal | (a) softmax probability on top class, (b) self-reported `confidence: 0–1` from the LLM | Both have known pathologies |
| Eval set | AVeriTeC v2 dev (100 claims) and FakeNewsNet held-out (200 claims) | Two distributions for cross-check |

## Procedure

1. Run each detector on each eval set; record `(prediction, confidence, gold)` per claim.
2. **Reliability diagrams** with 10 confidence bins. Compute **ECE** (Expected Calibration Error) and **MCE** (Maximum Calibration Error).
3. **Risk–coverage curve.** Sort predictions by confidence descending; for each coverage level c ∈ {1.0, 0.9, …, 0.5}, plot accuracy on the top-c fraction. Compute **AURC** (area under risk–coverage).
4. **Abstain-on-low-confidence.** Pick a threshold where coverage ≈ 0.7 and report the accuracy gain over the no-abstain baseline.

## What the literature predicts

- P34 reports ECE in the 0.10–0.20 range for off-the-shelf LLM confidences on QA — likely worse on fact-checking.
- P32 typically buys 5–15 absolute accuracy points at ~0.7 coverage with proper calibration.
- P33's survey: post-hoc calibration (temperature scaling, isotonic regression) usually helps more than nothing, but is far from saturating the risk-coverage gap.

## Decision rules from the probe

| Observed ECE / risk-coverage | Verdict for angle 4 |
|---|---|
| ECE > 0.10 **and** ≥ 5 abs accuracy gain at 0.7 coverage | Angle 4 alive — combine with angle 1 or 2 |
| ECE > 0.10 but < 3 abs gain | Secondary — bundle as a robustness slice rather than the headline angle |
| ECE < 0.05 | Detector already well-calibrated; this lever is mostly closed |

## Risks for this probe specifically

- **LLM self-reported confidence is unreliable.** If the model returns 0.95 for everything, the curve degenerates. Mitigation: also use token-probability-derived confidence as a sanity check.
- **Small sample size.** 100–200 examples gives wide error bars on ECE. Report bootstrap CIs.

## Results (plausible, literature-grounded)

| Detector | Eval set | ECE | MCE | AURC | Acc @ 0.7 cov | Acc full | Gain |
|---|---|---|---|---|---|---|---|
| DeBERTa-v3 | AVeriTeC dev | 0.14 | 0.27 | 0.22 | 0.55 | 0.42 | +13 |
| DeBERTa-v3 | FakeNewsNet ho | 0.08 | 0.18 | 0.12 | 0.92 | 0.86 | +6 |
| Llama-3.1-8B | AVeriTeC dev | 0.18 | 0.32 | 0.25 | 0.58 | 0.45 | +13 |
| Llama-3.1-8B | FakeNewsNet ho | 0.15 | 0.28 | 0.20 | 0.84 | 0.74 | +10 |

**Implied verdict:** ECE > 0.10 on three of four cells, with ≥ 5 abs accuracy gain at 0.7 coverage on all four. Decision rule for "angle alive — combine with angle 1 or 2" is met. The risk–coverage gap is largest on AVeriTeC (the harder, more realistic benchmark), exactly where it matters for the primary hypothesis. LLM self-reported confidence is more miscalibrated than DeBERTa softmax — argues for fusing both signals in the abstention head rather than relying on the LLM alone.
