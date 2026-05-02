from misinfo.decompose.llm_decomposer import LLMDecomposer, _DecomposerOutput
from misinfo.inference.mock_backend import MockBackend
from misinfo.schemas import SubQuestion


def test_decomposer_caps_at_max_questions():
    def factory(_prompt, schema):
        assert schema is _DecomposerOutput
        return _DecomposerOutput(
            questions=[
                SubQuestion(question="q1"),
                SubQuestion(question="q2"),
                SubQuestion(question="q3"),
                SubQuestion(question="q4"),
            ]
        )

    d = LLMDecomposer(MockBackend(response_factory=factory))
    out = d.decompose("a claim", max_questions=2)
    assert len(out) == 2
    assert out[0].question == "q1"
