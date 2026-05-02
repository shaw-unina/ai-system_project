"""Pipeline-stage protocols. Implementations land in Phase 5+."""
from __future__ import annotations

from typing import Protocol, runtime_checkable

from misinfo.schemas import (
    AggregatorOutput,
    EvidenceRef,
    QuestionAnswer,
    SubQuestion,
    Verdict,
)


@runtime_checkable
class Decomposer(Protocol):
    """claim text → list of sub-questions."""

    def decompose(self, claim: str, *, max_questions: int = 3) -> list[SubQuestion]: ...


@runtime_checkable
class Retriever(Protocol):
    """sub-question → ranked evidence list (already cut to top_k)."""

    def retrieve(self, query: str, *, top_k: int = 5) -> list[EvidenceRef]: ...


@runtime_checkable
class Answerer(Protocol):
    """(sub-question, evidence) → per-question answer."""

    def answer(self, question: SubQuestion, evidence: list[EvidenceRef]) -> QuestionAnswer: ...


@runtime_checkable
class Aggregator(Protocol):
    """List of per-question answers → pre-abstention verdict."""

    def aggregate(self, claim: str, answers: list[QuestionAnswer]) -> AggregatorOutput: ...


@runtime_checkable
class AbstentionHead(Protocol):
    """Pre-abstention output + retrieval signals → final calibrated confidence.

    Returns (final_verdict_label, confidence). The orchestrator overrides the verdict
    label to "Abstain" when confidence < tau.
    """

    def score(
        self,
        aggregator_output: AggregatorOutput,
        retrieval_signals: dict[str, float],
    ) -> tuple[str, float]: ...


@runtime_checkable
class FactChecker(Protocol):
    """Top-level orchestrator. The only public API the FastAPI service wraps."""

    def verify(self, claim: str) -> Verdict: ...

    def batch_verify(self, claims: list[str]) -> list[Verdict]: ...
