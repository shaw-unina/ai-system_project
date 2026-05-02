"""τ override: low-confidence verdicts become Abstain end-to-end."""
from __future__ import annotations

from misinfo.decompose.llm_decomposer import LLMDecomposer, _DecomposerOutput
from misinfo.inference.mock_backend import MockBackend
from misinfo.pipeline.orchestrator import RAGFactChecker
from misinfo.retrieve.bm25 import BM25Retriever
from misinfo.retrieve.corpus import EvidenceCorpus
from misinfo.schemas import AggregatorOutput, QuestionAnswer, SubQuestion
from misinfo.verify.aggregator import LLMAggregator
from misinfo.verify.answerer import LLMAnswerer


def _factory_low_conf(_prompt, schema):
    if schema is _DecomposerOutput:
        return _DecomposerOutput(questions=[SubQuestion(question="q?")])
    if schema is QuestionAnswer:
        return QuestionAnswer(question="q", answer="a", evidence=[])
    if schema is AggregatorOutput:
        return AggregatorOutput(
            verdict="Supported", confidence=0.3, rationale="weak signal", evidence=[]
        )
    return schema()


def _build(tau):
    llm = MockBackend(response_factory=_factory_low_conf)
    return RAGFactChecker(
        decomposer=LLMDecomposer(llm),
        retriever=BM25Retriever(EvidenceCorpus()),
        answerer=LLMAnswerer(llm),
        aggregator=LLMAggregator(llm),
        backend_id="mock",
        model_id=llm.model_id,
        abstain_threshold=tau,
    )


def test_tau_above_confidence_yields_abstain():
    fc = _build(tau=0.5)
    v = fc.verify("any claim")
    assert v.verdict == "Abstain"
    assert v.confidence == 0.3


def test_tau_below_confidence_passes_through():
    fc = _build(tau=0.1)
    v = fc.verify("any claim")
    assert v.verdict == "Supported"
