from misinfo.abstention.retrieval_gated import RetrievalGatedHead
from misinfo.schemas import AggregatorOutput


def _agg(c: float = 0.8) -> AggregatorOutput:
    return AggregatorOutput(verdict="Supported", confidence=c, rationale="x")


def test_low_coverage_zeros_confidence():
    h = RetrievalGatedHead(coverage_min=0.5, top1_min=0.3)
    label, p = h.score(_agg(0.9), {"evidence_coverage": 0.1, "mean_top1": 0.9})
    assert label == "Supported"  # head doesn't relabel
    assert p == 0.0


def test_high_signals_pass_through():
    h = RetrievalGatedHead(coverage_min=0.5, top1_min=0.3)
    _, p = h.score(_agg(0.9), {"evidence_coverage": 0.8, "mean_top1": 0.7})
    assert p == 0.9


def test_save_load_roundtrip(tmp_path):
    h = RetrievalGatedHead(coverage_min=0.6, top1_min=0.4)
    p = tmp_path / "r.json"
    h.save(p)
    loaded = RetrievalGatedHead.load(p)
    assert loaded.coverage_min == 0.6
    assert loaded.top1_min == 0.4
