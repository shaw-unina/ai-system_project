import numpy as np

from misinfo.abstention.base import CalibrationRecord
from misinfo.abstention.fusion import LogisticFusionHead
from misinfo.schemas import AggregatorOutput


def test_fusion_learns_retrieval_signal():
    """Construct data where verifier confidence is uninformative noise but
    evidence_coverage perfectly predicts correctness. The fitted head should
    rank claims by coverage, not by verifier confidence.
    """
    rng = np.random.default_rng(0)
    records = []
    for _ in range(400):
        c = float(rng.uniform())  # uninformative
        cov = float(rng.uniform())
        correct = bool(rng.random() < cov)  # truth is in coverage
        records.append(CalibrationRecord(c, 0.5, cov, correct))

    h = LogisticFusionHead()
    h.fit(records)

    # High-coverage example should score above low-coverage one
    agg = AggregatorOutput(verdict="Supported", confidence=0.5, rationale="x")
    _, p_low = h.score(agg, {"mean_top1": 0.5, "evidence_coverage": 0.05})
    _, p_high = h.score(agg, {"mean_top1": 0.5, "evidence_coverage": 0.95})
    assert p_high > p_low


def test_fusion_save_load(tmp_path):
    rng = np.random.default_rng(1)
    records = [
        CalibrationRecord(rng.uniform(), rng.uniform(), rng.uniform(), bool(rng.integers(2)))
        for _ in range(100)
    ]
    h = LogisticFusionHead()
    h.fit(records)
    path = tmp_path / "fusion.joblib"
    h.save(path)
    loaded = LogisticFusionHead.load(path)
    agg = AggregatorOutput(verdict="Supported", confidence=0.6, rationale="x")
    sig = {"mean_top1": 0.5, "evidence_coverage": 0.5}
    assert loaded.score(agg, sig)[1] == h.score(agg, sig)[1]
