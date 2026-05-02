"""Reliability-diagram primitives. Reuses metrics.risk_coverage for risk curves."""
from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np

from misinfo.eval.metrics import risk_coverage


@dataclass(frozen=True)
class ReliabilityBin:
    lo: float
    hi: float
    n: int
    confidence: float
    accuracy: float


def reliability_bins(
    confidences: Sequence[float],
    correct: Sequence[bool],
    n_bins: int = 10,
) -> list[ReliabilityBin]:
    confs = np.asarray(confidences, dtype=float)
    corr = np.asarray(correct, dtype=float)
    if confs.size == 0:
        return []
    edges = np.linspace(0.0, 1.0, n_bins + 1)
    bin_idx = np.clip(np.digitize(confs, edges, right=True) - 1, 0, n_bins - 1)
    out: list[ReliabilityBin] = []
    for b in range(n_bins):
        mask = bin_idx == b
        n_b = int(mask.sum())
        if n_b == 0:
            out.append(ReliabilityBin(float(edges[b]), float(edges[b + 1]), 0, 0.0, 0.0))
        else:
            out.append(
                ReliabilityBin(
                    lo=float(edges[b]),
                    hi=float(edges[b + 1]),
                    n=n_b,
                    confidence=float(confs[mask].mean()),
                    accuracy=float(corr[mask].mean()),
                )
            )
    return out


def risk_coverage_curve(
    confidences: Sequence[float],
    correct: Sequence[bool],
) -> list[tuple[float, float]]:
    coverage, risk = risk_coverage(confidences, correct)
    return list(zip([float(c) for c in coverage], [float(r) for r in risk], strict=True))
