"""Eval result containers."""
from __future__ import annotations

from datetime import datetime, timezone

from pydantic import BaseModel, Field

from misinfo.schemas import Verdict


class ClaimResult(BaseModel):
    claim_id: str
    claim: str
    gold_label: str
    verdict: Verdict
    correct: bool
    latency_ms: float | None = None


class AggregateMetrics(BaseModel):
    n: int
    accuracy: float
    f1_macro: float
    ece: float
    mce: float
    aurc: float
    accuracy_at_70_coverage: float
    averitec_recall_proxy: float
    abstention_rate: float


class SliceMetrics(BaseModel):
    name: str
    n: int
    metrics: AggregateMetrics


class Results(BaseModel):
    system: str
    dataset: str
    n_claims: int
    aggregate: AggregateMetrics
    slices: list[SliceMetrics] = Field(default_factory=list)
    per_claim: list[ClaimResult] = Field(default_factory=list)
    generated_at_utc: str = Field(
        default_factory=lambda: datetime.now(timezone.utc).isoformat()
    )
