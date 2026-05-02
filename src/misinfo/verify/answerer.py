"""LLM-backed Answerer."""
from __future__ import annotations

from misinfo.inference.base import LanguageModel
from misinfo.observability import traced
from misinfo.pipeline.prompts import load
from misinfo.schemas import EvidenceRef, QuestionAnswer, SubQuestion


def _evidence_block(evidence: list[EvidenceRef]) -> str:
    if not evidence:
        return "(no evidence retrieved)"
    lines = []
    for e in evidence:
        lines.append(f"[{e.source_id}] {e.span}")
    return "\n".join(lines)


class LLMAnswerer:
    def __init__(self, llm: LanguageModel) -> None:
        self._llm = llm
        self._template = load("answer")

    @traced("answer")
    def answer(self, question: SubQuestion, evidence: list[EvidenceRef]) -> QuestionAnswer:
        prompt = self._template.format(
            question=question.question,
            evidence_block=_evidence_block(evidence),
        )
        out = self._llm.generate_structured(
            prompt, QuestionAnswer, max_tokens=300, temperature=0.0
        )
        # Force the question text in case the model rewrites it
        return QuestionAnswer(
            question=question.question, answer=out.answer, evidence=out.evidence or evidence,
        )
