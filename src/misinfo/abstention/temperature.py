"""Scalar temperature scaling on verifier confidence.

Standard post-hoc calibrator (Guo et al. 2017) reduced to a 1-D scalar T fit by
NLL minimisation in log-odds space. We don't have full softmax logits from
Groq — only a single confidence in [0, 1] per claim — so this is a binary
re-mapping: σ(logit(p) / T).
"""
from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path

import numpy as np

from misinfo.abstention.base import CalibrationRecord
from misinfo.schemas import AggregatorOutput

_EPS = 1e-6


def _logit(p: np.ndarray) -> np.ndarray:
    p = np.clip(p, _EPS, 1.0 - _EPS)
    return np.log(p / (1.0 - p))


def _sigmoid(z: np.ndarray) -> np.ndarray:
    return 1.0 / (1.0 + np.exp(-z))


@dataclass
class TemperatureScalingHead:
    temperature: float = 1.0

    def fit(self, records: list[CalibrationRecord]) -> None:
        if not records:
            return
        confs = np.array([r.verifier_confidence for r in records], dtype=float)
        correct = np.array([1.0 if r.correct else 0.0 for r in records], dtype=float)
        z = _logit(confs)

        def nll(t: float) -> float:
            if t <= 0:
                return math.inf
            p = _sigmoid(z / t)
            p = np.clip(p, _EPS, 1.0 - _EPS)
            return float(-(correct * np.log(p) + (1.0 - correct) * np.log(1.0 - p)).mean())

        from scipy.optimize import minimize_scalar  # lazy

        res = minimize_scalar(nll, bounds=(0.05, 10.0), method="bounded")
        self.temperature = float(res.x)

    def score(
        self,
        aggregator_output: AggregatorOutput,
        retrieval_signals: dict[str, float],  # noqa: ARG002
    ) -> tuple[str, float]:
        z = _logit(np.array([aggregator_output.confidence]))
        p = float(_sigmoid(z / self.temperature)[0])
        return aggregator_output.verdict, p

    def save(self, path: str | Path) -> None:
        Path(path).write_text(json.dumps({"temperature": self.temperature}))

    @classmethod
    def load(cls, path: str | Path) -> "TemperatureScalingHead":
        data = json.loads(Path(path).read_text())
        return cls(temperature=float(data["temperature"]))
