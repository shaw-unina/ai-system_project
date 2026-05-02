from misinfo.inference.mock_backend import MockBackend
from misinfo.schemas import AggregatorOutput, QuestionAnswer
from misinfo.verify.aggregator import LLMAggregator


def test_aggregator_passes_through_llm_output():
    def factory(_prompt, schema):
        assert schema is AggregatorOutput
        return AggregatorOutput(
            verdict="Refuted", confidence=0.6, rationale="conflict in answers", evidence=[]
        )

    agg = LLMAggregator(MockBackend(response_factory=factory))
    out = agg.aggregate(
        "claim",
        [QuestionAnswer(question="q", answer="a", evidence=[])],
    )
    assert out.verdict == "Refuted"
    assert out.confidence == 0.6
