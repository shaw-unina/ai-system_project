import math

import numpy as np

from misinfo.abstention.base import CalibrationRecord
from misinfo.abstention.temperature import TemperatureScalingHead
from misinfo.schemas import AggregatorOutput


def _records_overconfident(n: int = 200, seed: int = 0) -> list[CalibrationRecord]:
    """Confidences clustered near 0.9 but only ~60% correct → T > 1 expected."""
    rng = np.random.default_rng(seed)
    out = []
    for _ in range(n):
        c = float(np.clip(rng.normal(0.9, 0.05), 0.05, 0.95))
        correct = bool(rng.random() < 0.6)
        out.append(CalibrationRecord(c, 0.5, 0.5, correct))
    return out


def test_temperature_fit_reduces_nll():
    records = _records_overconfident()
    h = TemperatureScalingHead(temperature=1.0)

    def nll(t: float) -> float:
        h.temperature = t
        total = 0.0
        for r in records:
            agg = AggregatorOutput(
                verdict="Supported", confidence=r.verifier_confidence, rationale="x"
            )
            _, p = h.score(agg, {})
            p = max(min(p, 1 - 1e-6), 1e-6)
            total += -(math.log(p) if r.correct else math.log(1 - p))
        return total / len(records)

    before = nll(1.0)
    h.fit(records)
    after = nll(h.temperature)
    assert after <= before + 1e-9


def test_temperature_save_load_roundtrip(tmp_path):
    h = TemperatureScalingHead(temperature=2.5)
    p = tmp_path / "t.json"
    h.save(p)
    loaded = TemperatureScalingHead.load(p)
    assert math.isclose(loaded.temperature, 2.5)
