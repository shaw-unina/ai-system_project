"""LLM-backed Aggregator."""
from __future__ import annotations

from misinfo.inference.base import LanguageModel
from misinfo.observability import traced
from misinfo.pipeline.prompts import load
from misinfo.schemas import AggregatorOutput, QuestionAnswer


def _qa_block(answers: list[QuestionAnswer]) -> str:
    if not answers:
        return "(no sub-questions answered)"
    lines = []
    for i, qa in enumerate(answers, start=1):
        evid = ", ".join(e.source_id for e in qa.evidence) or "—"
        lines.append(f"Q{i}: {qa.question}\nA{i}: {qa.answer}\nEvidence used: {evid}")
    return "\n\n".join(lines)


class LLMAggregator:
    def __init__(self, llm: LanguageModel) -> None:
        self._llm = llm
        self._template = load("aggregate")

    @traced("aggregate")
    def aggregate(self, claim: str, answers: list[QuestionAnswer]) -> AggregatorOutput:
        prompt = self._template.format(claim=claim, qa_block=_qa_block(answers))
        return self._llm.generate_structured(
            prompt, AggregatorOutput, max_tokens=500, temperature=0.0
        )
