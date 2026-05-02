"""Shared API-test helpers. Imported (not auto-loaded) by individual test files."""
from __future__ import annotations

from typing import Any

from misinfo.abstention.identity import IdentityAbstentionHead
from misinfo.decompose.llm_decomposer import LLMDecomposer, _DecomposerOutput
from misinfo.inference.mock_backend import MockBackend
from misinfo.pipeline.orchestrator import RAGFactChecker
from misinfo.retrieve.bm25 import BM25Retriever
from misinfo.retrieve.corpus import EvidenceCorpus
from misinfo.schemas import AggregatorOutput, QuestionAnswer, SubQuestion
from misinfo.verify.aggregator import LLMAggregator
from misinfo.verify.answerer import LLMAnswerer


def _factory(verdict: str = "Supported", confidence: float = 0.85):
    def make(_prompt: str, schema: type):
        if schema is _DecomposerOutput:
            return _DecomposerOutput(questions=[SubQuestion(question="q?")])
        if schema is QuestionAnswer:
            return QuestionAnswer(question="q", answer="a", evidence=[])
        if schema is AggregatorOutput:
            return AggregatorOutput(
                verdict=verdict,  # type: ignore[arg-type]
                confidence=confidence,
                rationale="mock rationale",
                evidence=[],
            )
        return schema()  # type: ignore[call-arg]

    return make


def build_mock_factchecker(*, verdict: str = "Supported", confidence: float = 0.85,
                           tau: float | None = None) -> Any:
    llm = MockBackend(response_factory=_factory(verdict=verdict, confidence=confidence))
    return RAGFactChecker(
        decomposer=LLMDecomposer(llm),
        retriever=BM25Retriever(EvidenceCorpus()),
        answerer=LLMAnswerer(llm),
        aggregator=LLMAggregator(llm),
        abstention=IdentityAbstentionHead(),
        backend_id="mock",
        model_id=llm.model_id,
        abstain_threshold=tau,
    )


def make_test_app(**fc_kwargs):
    """Build a fresh FastAPI app wired to a MockBackend FactChecker."""
    from misinfo.services import deps
    from misinfo.services.api import create_app
    from misinfo.services.metrics import METRICS

    fc = build_mock_factchecker(**fc_kwargs)
    deps.set_factchecker_factory(lambda: fc)
    METRICS.reset()
    return create_app()
