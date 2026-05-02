from misinfo.eval.harness import run_eval
from misinfo.eval.reports import render_markdown
from misinfo.schemas import Verdict, VerdictMetadata


class _StubChecker:
    def verify(self, claim):
        verdict = "Supported" if "true" in claim.lower() else "Refuted"
        return Verdict(
            verdict=verdict,
            confidence=0.8,
            evidence=[],
            rationale="stub",
            metadata=VerdictMetadata(backend="mock", model_id="m"),
        )


def test_run_eval_aggregates_correctly():
    dataset = [
        {"claim_id": "1", "claim": "this is true", "label": "Supported"},
        {"claim_id": "2", "claim": "this is false", "label": "Refuted"},
        {"claim_id": "3", "claim": "another true thing", "label": "Refuted"},
    ]
    r = run_eval(_StubChecker(), dataset, system="stub", dataset_name="t")
    assert r.n_claims == 3
    assert 0.0 <= r.aggregate.accuracy <= 1.0
    assert r.aggregate.n == 3
    md = render_markdown(r)
    assert "Eval report" in md and "stub" in md
