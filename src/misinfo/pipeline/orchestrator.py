"""RAGFactChecker — composes the four stages into a single Verdict."""
from __future__ import annotations

from misinfo.abstention.identity import IdentityAbstentionHead
from misinfo.config import get_settings
from misinfo.observability import current_trace_id, traced
from misinfo.pipeline.interfaces import (
    AbstentionHead,
    Aggregator,
    Answerer,
    Decomposer,
    Retriever,
)
from misinfo.repro import git_sha
from misinfo.schemas import EvidenceRef, QuestionAnswer, Verdict, VerdictMetadata


def _retrieval_signals(per_question_evidence: list[list[EvidenceRef]]) -> dict[str, float]:
    """Cheap retrieval-quality signals fed to the abstention head.

    - mean top-1 score
    - fraction of sub-questions with at least one evidence document
    """
    if not per_question_evidence:
        return {"mean_top1": 0.0, "evidence_coverage": 0.0}
    top1 = []
    covered = 0
    for ev in per_question_evidence:
        if ev:
            top1.append(ev[0].score)
            covered += 1
    return {
        "mean_top1": float(sum(top1) / len(top1)) if top1 else 0.0,
        "evidence_coverage": covered / len(per_question_evidence),
    }


class RAGFactChecker:
    """End-to-end orchestrator. Public surface: verify(claim) → Verdict."""

    def __init__(
        self,
        decomposer: Decomposer,
        retriever: Retriever,
        answerer: Answerer,
        aggregator: Aggregator,
        abstention: AbstentionHead | None = None,
        *,
        backend_id: str = "groq",
        model_id: str = "",
        model_version: str | None = None,
        top_k: int = 5,
        max_questions: int = 3,
        abstain_threshold: float | None = None,
    ) -> None:
        self._decomposer = decomposer
        self._retriever = retriever
        self._answerer = answerer
        self._aggregator = aggregator
        self._abstention = abstention or IdentityAbstentionHead()
        self._backend_id = backend_id
        self._model_id = model_id
        self._model_version = model_version
        self._top_k = top_k
        self._max_questions = max_questions
        self._tau = abstain_threshold
        self.last_signals: dict[str, float] = {}

    @traced("verify")
    def verify(self, claim: str) -> Verdict:
        s = get_settings()
        questions = self._decomposer.decompose(claim, max_questions=self._max_questions)
        per_q_evidence: list[list[EvidenceRef]] = []
        answers: list[QuestionAnswer] = []
        for q in questions:
            evidence = self._retriever.retrieve(q.question, top_k=self._top_k)
            per_q_evidence.append(evidence)
            answers.append(self._answerer.answer(q, evidence))

        aggregated = self._aggregator.aggregate(claim, answers)
        signals = _retrieval_signals(per_q_evidence)
        self.last_signals = signals
        label, confidence = self._abstention.score(aggregated, signals)
        rationale = aggregated.rationale
        if self._tau is not None and confidence < self._tau:
            label = "Abstain"
            reasons = ["confidence below threshold"]
            if signals.get("evidence_coverage", 1.0) < 0.5:
                reasons.append("retrieval coverage low")
            if signals.get("mean_top1", 1.0) < 0.3:
                reasons.append("evidence weakly relevant")
            rationale = "Abstained: " + "; ".join(reasons) + "."

        # Flatten and dedupe evidence across the three sub-questions
        seen: set[str] = set()
        flat_evidence: list[EvidenceRef] = []
        for ev_list in per_q_evidence:
            for e in ev_list:
                if e.source_id not in seen:
                    flat_evidence.append(e)
                    seen.add(e.source_id)

        return Verdict(
            verdict=label,  # type: ignore[arg-type]
            confidence=confidence,
            evidence=flat_evidence,
            rationale=rationale,
            metadata=VerdictMetadata(
                backend=self._backend_id,
                model_id=self._model_id,
                model_version=self._model_version,
                seed=s.random_seed,
                temperature=0.0,
                config_hash=str(git_sha() or ""),
                langfuse_trace_id=current_trace_id(),
            ),
        )

    def batch_verify(self, claims: list[str]) -> list[Verdict]:
        return [self.verify(c) for c in claims]
