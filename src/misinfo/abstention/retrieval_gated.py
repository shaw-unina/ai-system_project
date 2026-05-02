"""Hard-rule abstention based on retrieval-quality signals.

If the retriever didn't surface enough decent evidence, force confidence to 0
(which the orchestrator will translate to Abstain via τ). Otherwise pass the
verifier's confidence through unchanged.

Thresholds `(c_min, s_min)` are fitted by 2-D grid search on a held-out fold to
maximise F1 at the target coverage.
"""
from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path

from misinfo.abstention.base import CalibrationRecord
from misinfo.schemas import AggregatorOutput


@dataclass
class RetrievalGatedHead:
    coverage_min: float = 0.5
    top1_min: float = 0.0

    def fit(self, records: list[CalibrationRecord]) -> None:
        if not records:
            return
        best = (-1.0, self.coverage_min, self.top1_min)
        cov_grid = [0.0, 0.25, 0.5, 0.75, 1.0]
        top1_grid = [0.0, 0.1, 0.25, 0.5, 0.75]
        for c in cov_grid:
            for s in top1_grid:
                gated_correct = 0
                gated_total = 0
                for r in records:
                    if r.evidence_coverage < c or r.mean_top1 < s:
                        continue  # would be abstained
                    gated_total += 1
                    if r.correct:
                        gated_correct += 1
                if gated_total < max(1, len(records) // 5):
                    continue  # too aggressive: skip
                acc = gated_correct / gated_total
                if acc > best[0]:
                    best = (acc, c, s)
        _, self.coverage_min, self.top1_min = best

    def score(
        self,
        aggregator_output: AggregatorOutput,
        retrieval_signals: dict[str, float],
    ) -> tuple[str, float]:
        cov = float(retrieval_signals.get("evidence_coverage", 0.0))
        top1 = float(retrieval_signals.get("mean_top1", 0.0))
        if cov < self.coverage_min or top1 < self.top1_min:
            return aggregator_output.verdict, 0.0
        return aggregator_output.verdict, aggregator_output.confidence

    def save(self, path: str | Path) -> None:
        Path(path).write_text(
            json.dumps({"coverage_min": self.coverage_min, "top1_min": self.top1_min})
        )

    @classmethod
    def load(cls, path: str | Path) -> "RetrievalGatedHead":
        data = json.loads(Path(path).read_text())
        return cls(
            coverage_min=float(data["coverage_min"]),
            top1_min=float(data["top1_min"]),
        )
