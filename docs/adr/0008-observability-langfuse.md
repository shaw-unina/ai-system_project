# ADR-0008 — Observability: Langfuse v2 self-hosted

**Status:** Accepted
**Date:** 2026-05-01

## Context

Switching the inference backend to Groq (ADR-0002) trades bit-identical reproducibility for speed and developer ergonomics. To preserve auditability we need to capture every LLM call (prompt, response, model id and version, latency, token counts, cost) and every pipeline stage (input, output, parent trace). Phase 2 NFR-Repro and NFR-Trans-1/2 motivate this directly.

## Decision

- **Default deployment: Langfuse Cloud** (`https://cloud.langfuse.com`). No infra cost, instant onboarding, free tier covers our volume.
- **Self-hosted fallback retained:** `docker-compose.yml` ships `langfuse/langfuse:2` + `postgres:15` so a privacy-sensitive deployment can swap by setting `LANGFUSE_HOST` to the local URL. No code change required — `LanguageModel` and `traced(...)` are agnostic to host.
- Wire `@observe()` from `langfuse.decorators` through a thin project wrapper `misinfo.observability.traced(...)` so all stages and backends emit nested spans.
- `traced(...)` is a **no-op** when `LANGFUSE_HOST` is unset — keeps unit tests offline.
- `Verdict.metadata.langfuse_trace_id` is populated when tracing is active, giving every Verdict a UI-clickable lineage.
- Phase 7 evaluations publish runs as Langfuse **datasets**, replacing ad-hoc CSVs as the canonical record.
- Langfuse v3 (6 containers) is a documented future upgrade path; not adopted for this project's lifetime.

## Consequences

- Strong observability without operational overhead.
- Reproducibility narrative becomes "every run is replayable from its trace + cache" rather than "bit-identical numbers".
- One more dep group (`inference` extras add `langfuse>=2,<3`).
- **Default Cloud means trace data also leaves the box** (Langfuse SaaS sees prompts/responses, in addition to Groq seeing them). Acceptable for the project's public-AVeriTeC scope; flagged in [LIMITATIONS.md](../LIMITATIONS.md). Switching to the self-hosted stack reverts the trace path to local-only.

## Alternatives considered

- **OpenTelemetry + Grafana / Jaeger.** Generic; requires more wiring; no LLM-specific UI for prompts/datasets/evals.
- **LangSmith.** Hosted only, paid for non-trivial usage, OpenAI-flavoured posture.
- **Print-based logging.** Cheap, but no nested-trace UI, no prompt versioning, no dataset evals.
- **Phoenix (Arize).** Strong on production observability; we don't yet need that scope.
- **Langfuse v3.** 6-container footprint is overkill for the project; revisit on graduation.
