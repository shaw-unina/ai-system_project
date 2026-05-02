"""End-to-end orchestrator test using a scripted MockBackend."""
from __future__ import annotations

from misinfo.abstention.identity import IdentityAbstentionHead
from misinfo.decompose.llm_decomposer import LLMDecomposer, _DecomposerOutput
from misinfo.inference.mock_backend import MockBackend
from misinfo.pipeline.orchestrator import RAGFactChecker
from misinfo.retrieve.bm25 import BM25Retriever
from misinfo.retrieve.corpus import EvidenceCorpus
from misinfo.schemas import AggregatorOutput, QuestionAnswer, SubQuestion
from misinfo.verify.aggregator import LLMAggregator
from misinfo.verify.answerer import LLMAnswerer


def _factory(prompt: str, schema: type):
    if schema is _DecomposerOutput:
        return _DecomposerOutput(
            questions=[
                SubQuestion(question="Is paris the capital of france?"),
            ]
        )
    if schema is QuestionAnswer:
        return QuestionAnswer(question="q", answer="yes", evidence=[])
    if schema is AggregatorOutput:
        return AggregatorOutput(
            verdict="Supported", confidence=0.9, rationale="all answers agree", evidence=[]
        )
    return schema()


def test_orchestrator_end_to_end():
    corpus = EvidenceCorpus.from_iterable([
        {"source_id": "wiki:paris", "text": "paris is the capital of france"},
    ])
    llm = MockBackend(response_factory=_factory)
    fc = RAGFactChecker(
        decomposer=LLMDecomposer(llm),
        retriever=BM25Retriever(corpus),
        answerer=LLMAnswerer(llm),
        aggregator=LLMAggregator(llm),
        abstention=IdentityAbstentionHead(),
        backend_id="mock",
        model_id=llm.model_id,
    )
    v = fc.verify("Paris is the capital of France.")
    assert v.verdict == "Supported"
    assert 0.0 <= v.confidence <= 1.0
    assert v.metadata.backend == "mock"
