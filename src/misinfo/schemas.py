"""Frozen pydantic models for the system contract.

The shape of `Verdict` is locked at Phase 4 close (per project scope).
Changes here require an ADR.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

VerdictLabel = Literal["Supported", "Refuted", "NotEnoughEvidence", "Abstain"]


class EvidenceRef(BaseModel):
    model_config = ConfigDict(extra="forbid")

    source_id: str
    url: str | None = None
    span: str
    score: float


class VerdictMetadata(BaseModel):
    model_config = ConfigDict(extra="allow")

    backend: str                          # e.g. "groq", "llama_cpp", "mock"
    model_id: str
    model_version: str | None = None
    seed: int | None = None
    temperature: float | None = None
    config_hash: str | None = None
    dataset_hash: str | None = None
    langfuse_trace_id: str | None = None
    generated_at_utc: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )


class Verdict(BaseModel):
    model_config = ConfigDict(extra="forbid")

    verdict: VerdictLabel
    confidence: float = Field(ge=0.0, le=1.0)
    evidence: list[EvidenceRef] = Field(default_factory=list)
    rationale: str
    metadata: VerdictMetadata


class SubQuestion(BaseModel):
    """Output of the Decomposer stage."""
    model_config = ConfigDict(extra="forbid")

    question: str
    rationale: str | None = None


class QuestionAnswer(BaseModel):
    """Output of the AnswerExtractor stage for a single sub-question."""
    model_config = ConfigDict(extra="forbid")

    question: str
    answer: str
    evidence: list[EvidenceRef] = Field(default_factory=list)


class AggregatorOutput(BaseModel):
    """Output of the Verdict aggregator before the Abstention head runs."""
    model_config = ConfigDict(extra="forbid")

    verdict: Literal["Supported", "Refuted", "NotEnoughEvidence"]
    confidence: float = Field(ge=0.0, le=1.0)
    rationale: str
    evidence: list[EvidenceRef] = Field(default_factory=list)
    extra: dict[str, Any] = Field(default_factory=dict)
