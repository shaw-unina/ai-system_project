# Architecture Decision Records

Each ADR captures one non-trivial architectural choice in the format:

```
# ADR-NNNN — Title

Status: Proposed | Accepted | Superseded by ADR-XXXX
Date: YYYY-MM-DD

## Context
What forces are at play?

## Decision
What we are doing.

## Consequences
What follows — good and bad.

## Alternatives considered
What we rejected and why.
```

ADRs are immutable once accepted. To change a decision, write a new ADR that
supersedes the old one and update both `Status` lines.

## Index

| ID | Title | Status |
|---|---|---|
| [0001](0001-pipeline-shape.md) | Pipeline shape: decomposition → per-question retrieval → verifier | Accepted |
| [0002](0002-inference-runtime.md) | Inference runtime: pluggable, Groq primary | Accepted |
| [0003](0003-verifier-model.md) | Verifier model: Llama-3.3-70B via Groq, Qwen-2.5-32B fallback | Accepted |
| [0004](0004-retrieval-hybrid.md) | Retrieval: hybrid BM25 + BGE-small with RRF | Accepted |
| [0005](0005-structured-output.md) | Structured output: JSON-mode + pydantic-validate retry | Accepted |
| [0006](0006-output-schema.md) | Output schema: `Verdict` from SCOPE.md, frozen | Accepted |
| [0007](0007-abstention-interface.md) | Abstention head: pluggable interface; impl deferred | Accepted |
| [0008](0008-observability-langfuse.md) | Observability: Langfuse v2 self-hosted | Accepted |
