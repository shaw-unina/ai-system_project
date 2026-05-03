"""Deterministic 3-way split: calibration / threshold / eval folds.

Used by the Phase 7 orchestrator to avoid τ-coverage double-dipping per
the calibration ADRs (0007, 0009).
"""
from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class ThreeWayFolds:
    calibration: tuple[int, ...]
    threshold: tuple[int, ...]
    eval: tuple[int, ...]


def three_way_split(
    n: int,
    *,
    calibration_frac: float = 0.4,
    threshold_frac: float = 0.2,
    eval_frac: float = 0.4,
    seed: int = 42,
) -> ThreeWayFolds:
    total = calibration_frac + threshold_frac + eval_frac
    if not (0.99 < total < 1.01):
        raise ValueError(f"fractions must sum to 1.0, got {total}")
    if n <= 0:
        return ThreeWayFolds((), (), ())
    rng = np.random.default_rng(seed)
    perm = rng.permutation(n)
    n_cal = int(round(calibration_frac * n))
    n_thr = int(round(threshold_frac * n))
    cal = tuple(int(i) for i in perm[:n_cal])
    thr = tuple(int(i) for i in perm[n_cal : n_cal + n_thr])
    evl = tuple(int(i) for i in perm[n_cal + n_thr :])
    return ThreeWayFolds(cal, thr, evl)


def select(items: Sequence, indices: Sequence[int]) -> list:
    return [items[i] for i in indices]
