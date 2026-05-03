# ADR-0002 — Inference runtime: pluggable, Groq primary

**Status:** Accepted
**Date:** 2026-05-01

## Context

Two hard constraints from the user:

1. Compute target is **CPU / Apple Silicon** (no discrete GPU).
2. The team wants developer ergonomics and short iteration cycles for Phases 5–7.

A local 7B Q4 model on M-series gets ~150 tok/s, putting the full 3-LLM-call pipeline near the p95 = 60 s ceiling. Not impossible, but tight enough to slow iteration substantially. Hosted inference (Groq) does ~500–1000 tok/s on the same models, dropping the per-claim latency to single-digit seconds and unlocking larger models (Llama-3.3-70B, Qwen-2.5-32B) on the free tier.

## Decision

The runtime is **pluggable** behind a `LanguageModel` Protocol (`src/misinfo/inference/base.py`). Three implementations:

- **`GroqBackend` (primary, default).** Hosted inference via the `groq` Python SDK. Reads `GROQ_API_KEY` from `Settings`. JSON-mode for structured output with one parse-failure retry.
- **`LlamaCppBackend` (deferred reference path).** Stub today. Implementation lands when a team member needs offline / privacy / leaderboard-submission runs. Tracked here so the contract stays complete.
- **`MockBackend` (tests).** Deterministic, offline.

Selection via env var `MISINFO_BACKEND ∈ {groq, llama_cpp, mock}`, default `groq`. Resolved by `inference.factory.get_backend()`.

## Consequences

- Phase 2 NFR-Lat-1 is comfortably satisfied (see updated latency table in [docs/ARCHITECTURE.md](../ARCHITECTURE.md)).
- Phase 2 NFR-Repro-1 amended: bit-identical reproducibility scoped to the optional `llama_cpp` backend; the Groq path records `(model_id, model_version, seed, temperature, langfuse_trace_id)` in `Verdict.metadata`.
- Phase 2 NFR-Priv-1 amended: under `MISINFO_BACKEND=groq`, claim text is sent to Groq.
- We cannot officially submit to the AVeriTeC-2 leaderboard (rules require open-weights on a single 23 GB GPU). We still evaluate against AVeriTeC v2 dev/test and report numbers.
- Network dependency at evaluation time. Mitigated by a response cache keyed on `(model_id, prompt_hash, seed, temperature)` (Phase 5).

## Alternatives considered

- **vLLM.** Best high-throughput open-weight serving, but no Apple Silicon support — rules it out for our team's dev box.
- **MLX.** ~30% faster than llama.cpp on Apple Silicon, but Apple-only. Rejected for portability (graders run Linux).
- **Ollama.** Excellent UX, but adds a daemon and complicates Docker packaging. We can re-evaluate if the team prefers.
- **Local-only llama.cpp.** Originally proposed; rejected as primary because of the latency squeeze. Kept as the reference path.
