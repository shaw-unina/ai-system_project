# ADR-0005 — Structured output: JSON-mode with pydantic-validate retry

**Status:** Accepted
**Date:** 2026-05-01

## Context

Every pipeline stage emits a typed pydantic model. Free-form prompting + regex parsing is fragile on small models; on hosted Groq inference we have native JSON-mode available.

## Decision

- All `generate_structured(...)` calls use `response_format={"type": "json_object"}` and append the schema's JSON Schema to the prompt.
- The result is parsed with `model.model_validate_json(...)`. On `ValidationError` or `JSONDecodeError`, retry once. On the second failure, raise.
- The local `LlamaCppBackend` (deferred) will use GBNF grammars for the same purpose.

## Consequences

- Tight contract between LLM output and downstream code — fewer parse-error rabbit holes.
- One extra retry per call in the worst case; latency cost is small.
- Schema changes propagate automatically (the JSON Schema is generated from the pydantic model).

## Alternatives considered

- **GBNF grammars on Groq.** Not supported.
- **Outlines / Instructor libraries.** Add deps and complexity for a feature Groq's JSON-mode already provides on hosted inference.
- **Free-form + regex parse.** Fragile, especially on multi-question outputs.
