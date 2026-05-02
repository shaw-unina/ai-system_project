"""Calibrated abstention head Protocol + the calibration-record container.

Heads consume a `list[CalibrationRecord]` at fit time and `(AggregatorOutput,
retrieval_signals)` at score time. The orchestrator owns the τ-→-Abstain
override (see ADR-0007) so heads return a *calibrated confidence* and never the
"Abstain" label themselves.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol, runtime_checkable

from misinfo.schemas import AggregatorOutput


@dataclass(frozen=True)
class CalibrationRecord:
    verifier_confidence: float
    mean_top1: float
    evidence_coverage: float
    correct: bool


@runtime_checkable
class CalibratedAbstentionHead(Protocol):
    """Calibrated extension of `AbstentionHead`.

    Implementations must round-trip through `save` / `load` losslessly so a
    calibrated head can be re-used across Phase 7 runs without re-fitting.
    """

    def fit(self, records: list[CalibrationRecord]) -> None: ...
    def save(self, path: str | Path) -> None: ...
    @classmethod
    def load(cls, path: str | Path) -> "CalibratedAbstentionHead": ...
    def score(
        self,
        aggregator_output: AggregatorOutput,
        retrieval_signals: dict[str, float],
    ) -> tuple[str, float]: ...
