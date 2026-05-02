"""HTTP API request/response schemas (versioned).

Distinct from the internal `Verdict` (src/misinfo/schemas.py): the API surface
adds `disclosure`, `low_confidence`, `request_id`, and `latency_ms` per
NFR-Trans-2 and Phase 8 conventions.
"""
from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from misinfo.schemas import EvidenceRef, VerdictLabel, VerdictMetadata

MAX_CLAIM_CHARS = 4000
MAX_BATCH_CLAIMS = 100
LOW_CONFIDENCE_THRESHOLD = 0.5


class VerifyRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    claim: str = Field(min_length=1, max_length=MAX_CLAIM_CHARS)
    client_id: str | None = None


class BatchRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")

    claims: list[str] = Field(min_length=1, max_length=MAX_BATCH_CLAIMS)


class VerifyResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    verdict: VerdictLabel
    confidence: float
    evidence: list[EvidenceRef]
    rationale: str
    metadata: VerdictMetadata
    disclosure: Literal["ai_generated"] = "ai_generated"
    low_confidence: bool
    request_id: str
    latency_ms: float


class BatchResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    results: list[VerifyResponse]


class HealthResponse(BaseModel):
    status: Literal["ok"] = "ok"


class ReadyResponse(BaseModel):
    ready: bool
    backend: str
    head: str | None = None
    tau: float | None = None


class VersionResponse(BaseModel):
    name: str
    version: str
    git_sha: str | None = None
    model_id: str
    model_version: str | None = None


class ErrorEnvelope(BaseModel):
    error: str
    detail: str | None = None
    request_id: str | None = None
