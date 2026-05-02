"""Evaluation metrics: F1, ECE, MCE, AURC, accuracy@coverage. Pure NumPy."""
from __future__ import annotations

from collections.abc import Sequence

import numpy as np


def f1_macro(y_true: Sequence[str], y_pred: Sequence[str]) -> float:
    """Macro-averaged F1 across all distinct labels appearing in y_true ∪ y_pred."""
    if len(y_true) != len(y_pred):
        raise ValueError("y_true and y_pred must be same length")
    if not y_true:
        return 0.0
    labels = sorted(set(y_true) | set(y_pred))
    f1s: list[float] = []
    for lab in labels:
        tp = sum(1 for t, p in zip(y_true, y_pred, strict=True) if t == lab and p == lab)
        fp = sum(1 for t, p in zip(y_true, y_pred, strict=True) if t != lab and p == lab)
        fn = sum(1 for t, p in zip(y_true, y_pred, strict=True) if t == lab and p != lab)
        denom = (2 * tp + fp + fn)
        f1s.append(0.0 if denom == 0 else (2 * tp) / denom)
    return float(np.mean(f1s))


def accuracy(y_true: Sequence[str], y_pred: Sequence[str]) -> float:
    if not y_true:
        return 0.0
    correct = sum(1 for t, p in zip(y_true, y_pred, strict=True) if t == p)
    return correct / len(y_true)


def _ece_buckets(
    confidences: Sequence[float],
    correct: Sequence[bool],
    n_bins: int = 10,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Return (bin_acc, bin_conf, bin_weight) for `n_bins` equal-width bins on [0, 1]."""
    confs = np.asarray(confidences, dtype=float)
    corr = np.asarray(correct, dtype=float)
    if confs.size == 0:
        z = np.zeros(n_bins)
        return z, z, z
    edges = np.linspace(0.0, 1.0, n_bins + 1)
    bin_idx = np.clip(np.digitize(confs, edges, right=True) - 1, 0, n_bins - 1)
    bin_acc = np.zeros(n_bins)
    bin_conf = np.zeros(n_bins)
    bin_w = np.zeros(n_bins)
    for b in range(n_bins):
        mask = bin_idx == b
        if mask.any():
            bin_acc[b] = corr[mask].mean()
            bin_conf[b] = confs[mask].mean()
            bin_w[b] = mask.sum() / len(confs)
    return bin_acc, bin_conf, bin_w


def ece(confidences: Sequence[float], correct: Sequence[bool], n_bins: int = 10) -> float:
    """Expected Calibration Error (Naeini et al. 2015) with equal-width bins."""
    bin_acc, bin_conf, bin_w = _ece_buckets(confidences, correct, n_bins)
    return float(np.sum(bin_w * np.abs(bin_acc - bin_conf)))


def mce(confidences: Sequence[float], correct: Sequence[bool], n_bins: int = 10) -> float:
    """Maximum Calibration Error."""
    bin_acc, bin_conf, bin_w = _ece_buckets(confidences, correct, n_bins)
    populated = bin_w > 0
    if not populated.any():
        return 0.0
    return float(np.max(np.abs(bin_acc[populated] - bin_conf[populated])))


def risk_coverage(
    confidences: Sequence[float],
    correct: Sequence[bool],
) -> tuple[np.ndarray, np.ndarray]:
    """Return (coverage_grid, risk_grid) sorted by descending confidence.

    risk = 1 - accuracy on the top-fraction at each coverage level.
    """
    confs = np.asarray(confidences, dtype=float)
    corr = np.asarray(correct, dtype=float)
    if confs.size == 0:
        return np.array([0.0]), np.array([0.0])
    order = np.argsort(-confs)
    corr_sorted = corr[order]
    coverage = np.arange(1, len(confs) + 1) / len(confs)
    cumulative_correct = np.cumsum(corr_sorted)
    risk = 1.0 - cumulative_correct / np.arange(1, len(confs) + 1)
    return coverage, risk


def aurc(confidences: Sequence[float], correct: Sequence[bool]) -> float:
    """Area under the risk–coverage curve (lower is better)."""
    coverage, risk = risk_coverage(confidences, correct)
    if coverage.size < 2:
        return float(risk[0]) if risk.size else 0.0
    return float(np.trapezoid(risk, coverage))


def accuracy_at_coverage(
    confidences: Sequence[float],
    correct: Sequence[bool],
    coverage: float = 0.7,
) -> float:
    """Accuracy on the top-`coverage` fraction by confidence."""
    if not 0.0 < coverage <= 1.0:
        raise ValueError("coverage must be in (0, 1]")
    confs = np.asarray(confidences, dtype=float)
    corr = np.asarray(correct, dtype=float)
    if confs.size == 0:
        return 0.0
    order = np.argsort(-confs)
    n = max(1, int(round(len(confs) * coverage)))
    return float(corr[order[:n]].mean())


def averitec_recall_proxy(
    y_true: Sequence[str],
    y_pred: Sequence[str],
) -> float:
    """A recall-style proxy for the official AVeriTeC score.

    NOT the official Ev2R metric — that requires reference QA pairs we don't
    have. We report this as `averitec_recall_proxy` and document the caveat.
    """
    relevant = ("Supported", "Refuted")
    correct = 0
    total = 0
    for t, p in zip(y_true, y_pred, strict=True):
        if t in relevant:
            total += 1
            if t == p:
                correct += 1
    return correct / total if total else 0.0
