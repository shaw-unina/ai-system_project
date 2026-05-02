"""Logistic fusion of verifier confidence + retrieval signals → P(correct).

The realised research contribution: a learned head that decides whether to
trust the verifier on this claim, given how good retrieval looked. Phase 7's
primary system is `RAGFactChecker(abstention=LogisticFusionHead, tau=...)`.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from misinfo.abstention.base import CalibrationRecord
from misinfo.schemas import AggregatorOutput

_FEATURES = ("verifier_confidence", "mean_top1", "evidence_coverage")


def _row(r: CalibrationRecord) -> list[float]:
    return [r.verifier_confidence, r.mean_top1, r.evidence_coverage]


class LogisticFusionHead:
    def __init__(self, estimator: Any | None = None) -> None:
        self._estimator = estimator

    def fit(self, records: list[CalibrationRecord]) -> None:
        if not records:
            return
        from sklearn.linear_model import LogisticRegression  # lazy

        x = [_row(r) for r in records]
        y = [1 if r.correct else 0 for r in records]
        if len(set(y)) < 2:
            # All same class — degenerate; leave estimator unfit.
            return
        est = LogisticRegression(max_iter=1000)
        est.fit(x, y)
        self._estimator = est

    def score(
        self,
        aggregator_output: AggregatorOutput,
        retrieval_signals: dict[str, float],
    ) -> tuple[str, float]:
        if self._estimator is None:
            return aggregator_output.verdict, aggregator_output.confidence
        x = [[
            aggregator_output.confidence,
            float(retrieval_signals.get("mean_top1", 0.0)),
            float(retrieval_signals.get("evidence_coverage", 0.0)),
        ]]
        p = float(self._estimator.predict_proba(x)[0, 1])
        return aggregator_output.verdict, p

    def save(self, path: str | Path) -> None:
        import joblib  # lazy
        joblib.dump({"features": _FEATURES, "estimator": self._estimator}, Path(path))

    @classmethod
    def load(cls, path: str | Path) -> "LogisticFusionHead":
        import joblib  # lazy
        data = joblib.load(Path(path))
        return cls(estimator=data["estimator"])
