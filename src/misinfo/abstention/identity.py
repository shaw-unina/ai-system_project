"""Passthrough abstention head — Phase 5 stub.

Real heads land in Phase 6 (per ADR-0007). This stub exists so the orchestrator
runs end-to-end without an abstention strategy.
"""
from __future__ import annotations

from misinfo.schemas import AggregatorOutput


class IdentityAbstentionHead:
    def score(
        self,
        aggregator_output: AggregatorOutput,
        retrieval_signals: dict[str, float],
    ) -> tuple[str, float]:
        return aggregator_output.verdict, aggregator_output.confidence
