"""Run a FactChecker over a dataset and produce Results."""
from __future__ import annotations

import time
from collections.abc import Sequence
from typing import Any, Protocol

from misinfo.eval import metrics as M
from misinfo.eval.results import (
    AggregateMetrics,
    ClaimResult,
    Results,
    SliceMetrics,
)
from misinfo.schemas import Verdict


class _FactCheckerLike(Protocol):
    def verify(self, claim: str) -> Verdict: ...


class ClaimRecord(Protocol):
    """A dataset row. Either a dict-like with the required fields, or a typed
    object exposing them as attributes. We accept duck-typed dicts in practice."""


def _get(record: Any, field: str, default: Any = None) -> Any:
    if isinstance(record, dict):
        return record.get(field, default)
    return getattr(record, field, default)


def _aggregate(per_claim: list[ClaimResult]) -> AggregateMetrics:
    if not per_claim:
        return AggregateMetrics(
            n=0, accuracy=0.0, f1_macro=0.0, ece=0.0, mce=0.0, aurc=0.0,
            accuracy_at_70_coverage=0.0, averitec_recall_proxy=0.0, abstention_rate=0.0,
        )
    y_true = [r.gold_label for r in per_claim]
    y_pred = [r.verdict.verdict for r in per_claim]
    confs = [r.verdict.confidence for r in per_claim]
    correct = [r.correct for r in per_claim]
    abstain = sum(1 for r in per_claim if r.verdict.verdict == "Abstain")
    return AggregateMetrics(
        n=len(per_claim),
        accuracy=M.accuracy(y_true, y_pred),
        f1_macro=M.f1_macro(y_true, y_pred),
        ece=M.ece(confs, correct),
        mce=M.mce(confs, correct),
        aurc=M.aurc(confs, correct),
        accuracy_at_70_coverage=M.accuracy_at_coverage(confs, correct, 0.7),
        averitec_recall_proxy=M.averitec_recall_proxy(y_true, y_pred),
        abstention_rate=abstain / len(per_claim),
    )


def run_eval(
    factchecker: _FactCheckerLike,
    dataset: Sequence[Any],
    *,
    system: str = "rag",
    dataset_name: str = "unknown",
    slices: dict[str, list[int]] | None = None,
) -> Results:
    """Run `factchecker` over `dataset`. Each row must expose `claim_id`, `claim`, `label`."""
    per_claim: list[ClaimResult] = []
    for row in dataset:
        claim = _get(row, "claim")
        gold = _get(row, "label")
        cid = _get(row, "claim_id", default=str(len(per_claim)))
        t0 = time.perf_counter()
        verdict = factchecker.verify(claim)
        t1 = time.perf_counter()
        signals = dict(getattr(factchecker, "last_signals", {}) or {})
        per_claim.append(
            ClaimResult(
                claim_id=str(cid),
                claim=claim,
                gold_label=str(gold),
                verdict=verdict,
                correct=(verdict.verdict == gold),
                latency_ms=1000.0 * (t1 - t0),
                signals=signals,
            )
        )

    aggregate = _aggregate(per_claim)
    slice_results: list[SliceMetrics] = []
    if slices:
        for name, idxs in slices.items():
            subset = [per_claim[i] for i in idxs if i < len(per_claim)]
            slice_results.append(
                SliceMetrics(name=name, n=len(subset), metrics=_aggregate(subset))
            )

    return Results(
        system=system,
        dataset=dataset_name,
        n_claims=len(per_claim),
        aggregate=aggregate,
        slices=slice_results,
        per_claim=per_claim,
    )
