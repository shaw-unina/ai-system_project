# ADR-0003 — Verifier model

**Status:** Accepted
**Date:** 2026-05-01

## Context

We need a verifier capable of: (a) producing structured JSON output reliably, (b) handling 4-5k tokens of context per call (claim + evidence + question), (c) multi-hop reasoning across 3 sub-questions, (d) running fast enough on Groq's free tier to survive the Phase 7 evaluation volume. The Phase 1 literature (P07, P08) shows 7-8 B class models are competitive, but the leaderboard cap was a *hardware constraint* — accuracy keeps growing with scale.

## Decision

- **Primary:** `llama-3.3-70b-versatile` on Groq.
- **Fallback / cross-model parity:** `qwen/qwen-2.5-32b` on Groq.
- **Local reference (deferred):** Qwen-2.5-7B-Instruct Q4_K_M GGUF when `LlamaCppBackend` is implemented.

The same model serves both as the verifier and as the paraphraser for the LLM-paraphrase attack set (Phase 6) — separate prompts, single dependency.

## Consequences

- Larger model than the AVeriTeC-2 leaderboard cap → expected accuracy bump on multi-hop / numerical claims.
- Cross-model parity check (Llama vs Qwen) is a free Phase 7 ablation.
- If Groq deprecates either model name, swap in `Settings.groq_model` and record in metadata.

## Alternatives considered

- **GPT-4-class hosted via OpenAI.** Excellent quality, closed-weight, expensive, and the project posture is open-weight.
- **Mixtral 8x7B.** Strong but slower on Groq than Llama-3.3-70B and weaker on JSON-mode reliability.
- **Phi-3.5-mini-3.8B.** Fast but weaker on multi-hop. Possible local fallback for the deferred `LlamaCppBackend` path.
