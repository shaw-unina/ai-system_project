"""Paired-bootstrap CI + p-value for the H1 statistical battery.

`paired_bootstrap_diff` resamples claim indices with replacement, computes
`metric(y_true, y_a) - metric(y_true, y_b)` per resample, returns the point
estimate, a 95% CI, and a one-sided p-value for the null `diff ≤ 0`.
"""
from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass

import numpy as np


@dataclass(frozen=True)
class BootstrapResult:
    point: float
    ci_low: float
    ci_high: float
    p_value: float
    n_resamples: int


def paired_bootstrap_diff(
    metric_fn: Callable[[Sequence, Sequence], float],
    y_true: Sequence,
    y_a: Sequence,
    y_b: Sequence,
    *,
    n: int = 10_000,
    seed: int = 42,
    alpha: float = 0.05,
) -> BootstrapResult:
    """Paired bootstrap on `metric(a) - metric(b)`. One-sided p-value (H0: diff ≤ 0)."""
    if not (len(y_true) == len(y_a) == len(y_b)):
        raise ValueError("y_true, y_a, y_b must be same length")
    if not y_true:
        return BootstrapResult(0.0, 0.0, 0.0, 1.0, 0)

    yt = np.asarray(y_true)
    ya = np.asarray(y_a)
    yb = np.asarray(y_b)
    rng = np.random.default_rng(seed)
    m = len(yt)
    diffs = np.empty(n, dtype=float)
    for i in range(n):
        idx = rng.integers(0, m, size=m)
        diffs[i] = metric_fn(list(yt[idx]), list(ya[idx])) - metric_fn(list(yt[idx]), list(yb[idx]))
    point = float(metric_fn(list(yt), list(ya)) - metric_fn(list(yt), list(yb)))
    lo = float(np.quantile(diffs, alpha / 2))
    hi = float(np.quantile(diffs, 1 - alpha / 2))
    p = float((diffs <= 0).mean())
    return BootstrapResult(point, lo, hi, p, n)


def bootstrap_ci(
    metric_fn: Callable[[Sequence, Sequence], float],
    y_true: Sequence,
    y_pred: Sequence,
    *,
    n: int = 10_000,
    seed: int = 42,
    alpha: float = 0.05,
) -> tuple[float, float, float]:
    if not y_true:
        return 0.0, 0.0, 0.0
    yt = np.asarray(y_true)
    yp = np.asarray(y_pred)
    rng = np.random.default_rng(seed)
    m = len(yt)
    samples = np.empty(n, dtype=float)
    for i in range(n):
        idx = rng.integers(0, m, size=m)
        samples[i] = metric_fn(list(yt[idx]), list(yp[idx]))
    point = float(metric_fn(list(yt), list(yp)))
    lo = float(np.quantile(samples, alpha / 2))
    hi = float(np.quantile(samples, 1 - alpha / 2))
    return point, lo, hi


def holm_correct(p_values: Sequence[float]) -> list[float]:
    """Holm-Bonferroni correction. Returns adjusted p-values in original order."""
    p = np.asarray(p_values, dtype=float)
    m = len(p)
    if m == 0:
        return []
    order = np.argsort(p)
    adj = np.empty(m, dtype=float)
    running = 0.0
    for rank, idx in enumerate(order):
        v = (m - rank) * p[idx]
        running = max(running, min(v, 1.0))
        adj[idx] = running
    return adj.tolist()
