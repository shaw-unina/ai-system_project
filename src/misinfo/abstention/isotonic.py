"""Isotonic regression calibrator on verifier confidence.

Non-parametric, monotonic mapping from raw confidence to P(correct). Robust to
the shape of the miscalibration curve (sigmoid, S-shaped, etc.) at the cost of
needing more calibration data than temperature scaling.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from misinfo.abstention.base import CalibrationRecord
from misinfo.schemas import AggregatorOutput


class IsotonicCalibrationHead:
    def __init__(self, estimator: Any | None = None) -> None:
        self._estimator = estimator

    def fit(self, records: list[CalibrationRecord]) -> None:
        if not records:
            return
        from sklearn.isotonic import IsotonicRegression  # lazy

        confs = [r.verifier_confidence for r in records]
        correct = [1.0 if r.correct else 0.0 for r in records]
        est = IsotonicRegression(out_of_bounds="clip", y_min=0.0, y_max=1.0)
        est.fit(confs, correct)
        self._estimator = est

    def score(
        self,
        aggregator_output: AggregatorOutput,
        retrieval_signals: dict[str, float],  # noqa: ARG002
    ) -> tuple[str, float]:
        if self._estimator is None:
            return aggregator_output.verdict, aggregator_output.confidence
        p = float(self._estimator.predict([aggregator_output.confidence])[0])
        return aggregator_output.verdict, p

    def save(self, path: str | Path) -> None:
        import joblib  # lazy
        joblib.dump(self._estimator, Path(path))

    @classmethod
    def load(cls, path: str | Path) -> "IsotonicCalibrationHead":
        import joblib  # lazy
        return cls(estimator=joblib.load(Path(path)))
