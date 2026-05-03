# ADR-0006 — Output schema: `Verdict` from SCOPE.md, frozen

**Status:** Accepted
**Date:** 2026-05-01

## Context

Every consumer of the system (FastAPI in Phase 8, dashboard in Phase 10, batch CLI, eval harness in Phase 5) must agree on the `Verdict` shape. Project scope defined it; Phase 4 lands it as code.

## Decision

- `src/misinfo/schemas.py` defines `Verdict`, `EvidenceRef`, `VerdictMetadata`, plus the per-stage models `SubQuestion`, `QuestionAnswer`, `AggregatorOutput`.
- `Verdict.model_config = ConfigDict(extra="forbid")` to catch drift.
- The `verdict` label uses `Literal["Supported", "Refuted", "NotEnoughEvidence", "Abstain"]`. `Abstain` is a system action; `NotEnoughEvidence` is a verdict on the claim itself (per SCOPE.md).
- Schema changes require an entry in SCOPE.md "Amendments" and a new ADR superseding this one.

## Consequences

- Compile-time guarantees across modules.
- JSON Schema is auto-generated for Groq JSON-mode prompts and FastAPI OpenAPI docs.
- Adding a field is non-breaking (use a default); changing or removing a field requires a migration.

## Alternatives considered

- **TypedDict + manual validation.** Less ceremony but loses runtime validation and JSON-Schema generation.
- **Protobuf / Avro.** Overkill for an in-process Python service.
