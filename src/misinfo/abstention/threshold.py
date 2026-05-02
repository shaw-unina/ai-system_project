"""τ selection + calibration record extraction utilities."""
from __future__ import annotations

import json
from collections.abc import Sequence
from pathlib import Path

from misinfo.abstention.base import CalibrationRecord


def select_threshold_for_coverage(
    confidences: Sequence[float],
    target_coverage: float,
) -> float:
    """Pick τ such that fraction of inputs with confidence ≥ τ equals `target_coverage`.

    Returns the (1 − target_coverage)-quantile of the confidence distribution.
    With target_coverage=0.7, τ is set so 70% of inputs are accepted, 30% abstained.
    """
    if not 0.0 < target_coverage <= 1.0:
        raise ValueError("target_coverage must be in (0, 1]")
    if not confidences:
        return 0.0
    sorted_confs = sorted(confidences)
    drop = int(round((1.0 - target_coverage) * len(sorted_confs)))
    drop = min(drop, len(sorted_confs) - 1)
    return float(sorted_confs[drop])


def records_from_jsonl(path: str | Path) -> list[CalibrationRecord]:
    out: list[CalibrationRecord] = []
    with Path(path).open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            row = json.loads(line)
            out.append(
                CalibrationRecord(
                    verifier_confidence=float(row["verifier_confidence"]),
                    mean_top1=float(row.get("mean_top1", 0.0)),
                    evidence_coverage=float(row.get("evidence_coverage", 0.0)),
                    correct=bool(row["correct"]),
                )
            )
    return out
