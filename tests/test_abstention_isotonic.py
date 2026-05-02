import numpy as np

from misinfo.abstention.base import CalibrationRecord
from misinfo.abstention.isotonic import IsotonicCalibrationHead
from misinfo.schemas import AggregatorOutput


def test_isotonic_monotone_after_fit():
    rng = np.random.default_rng(0)
    records = []
    for _ in range(300):
        c = float(rng.uniform())
        # P(correct) = c — perfectly calibrated underlying truth
        correct = bool(rng.random() < c)
        records.append(CalibrationRecord(c, 0.5, 0.5, correct))

    h = IsotonicCalibrationHead()
    h.fit(records)

    xs = np.linspace(0.05, 0.95, 19)
    ys = []
    for x in xs:
        agg = AggregatorOutput(verdict="Supported", confidence=float(x), rationale="x")
        _, p = h.score(agg, {})
        ys.append(p)
    # Monotone non-decreasing
    diffs = np.diff(np.array(ys))
    assert (diffs >= -1e-9).all()


def test_isotonic_passthrough_when_unfit():
    h = IsotonicCalibrationHead()
    agg = AggregatorOutput(verdict="Refuted", confidence=0.42, rationale="x")
    label, p = h.score(agg, {})
    assert label == "Refuted"
    assert p == 0.42
