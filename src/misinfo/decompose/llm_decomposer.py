"""LLM-backed Decomposer."""
from __future__ import annotations

from pydantic import BaseModel, Field

from misinfo.inference.base import LanguageModel
from misinfo.observability import traced
from misinfo.pipeline.prompts import load
from misinfo.schemas import SubQuestion


class _DecomposerOutput(BaseModel):
    questions: list[SubQuestion] = Field(default_factory=list)


class LLMDecomposer:
    def __init__(self, llm: LanguageModel) -> None:
        self._llm = llm
        self._template = load("decompose")

    @traced("decompose")
    def decompose(self, claim: str, *, max_questions: int = 3) -> list[SubQuestion]:
        prompt = self._template.format(claim=claim, max_questions=max_questions)
        out = self._llm.generate_structured(
            prompt, _DecomposerOutput, max_tokens=400, temperature=0.0
        )
        return out.questions[:max_questions]
