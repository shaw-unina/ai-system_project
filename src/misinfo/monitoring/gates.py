"""Quality gates over an `eval.results.Results` object.

Gates are a YAML list of {name, metric, op, value} rows. `spread_le` is the
fairness-aware operator: max(slice_metric) − min(slice_metric) ≤ value.
"""
from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass, field
from pathlib import Path

import yaml

from misinfo.eval.results import Results

_OPS = {
    "le": (lambda observed, target: observed <= target, "≤"),
    "ge": (lambda observed, target: observed >= target, "≥"),
    "lt": (lambda observed, target: observed < target, "<"),
    "gt": (lambda observed, target: observed > target, ">"),
    "eq": (lambda observed, target: observed == target, "="),
}


@dataclass(frozen=True)
class Gate:
    name: str
    op: str
    value: float
    metric: str | None = None         # for aggregate metrics
    slice_metric: str | None = None   # for spread_le over slice metrics


@dataclass(frozen=True)
class ThresholdsConfig:
    gates: tuple[Gate, ...]


@dataclass(frozen=True)
class GateOutcome:
    gate: Gate
    passed: bool
    observed: float
    reason: str


@dataclass
class GateReport:
    outcomes: list[GateOutcome] = field(default_factory=list)

    @property
    def passed(self) -> bool:
        return all(o.passed for o in self.outcomes)

    def render_markdown(self) -> str:
        lines = ["# Quality gates", "",
                 f"**Overall:** {'PASS' if self.passed else 'FAIL'}", "",
                 "| gate | op | target | observed | passed | reason |",
                 "|---|---|---|---|---|---|"]
        for o in self.outcomes:
            sym = _OPS.get(o.gate.op, (None, o.gate.op))[1]
            lines.append(
                f"| {o.gate.name} | {sym} | {o.gate.value} | {o.observed:.4f} | "
                f"{'yes' if o.passed else 'no'} | {o.reason} |"
            )
        return "\n".join(lines) + "\n"


def _agg_value(results: Results, metric: str) -> float:
    if not hasattr(results.aggregate, metric):
        raise ValueError(f"unknown aggregate metric: {metric!r}")
    return float(getattr(results.aggregate, metric))


def _slice_spread(results: Results, slice_metric: str) -> float:
    if not results.slices:
        return 0.0
    values = []
    for s in results.slices:
        if not hasattr(s.metrics, slice_metric):
            raise ValueError(f"unknown slice metric: {slice_metric!r}")
        values.append(float(getattr(s.metrics, slice_metric)))
    if not values:
        return 0.0
    return float(max(values) - min(values))


def _evaluate(results: Results, gate: Gate) -> GateOutcome:
    if gate.op == "spread_le":
        if not gate.slice_metric:
            return GateOutcome(gate, False, 0.0, "spread_le requires slice_metric")
        observed = _slice_spread(results, gate.slice_metric)
        passed = observed <= gate.value
        reason = f"spread of {gate.slice_metric} = {observed:.4f}; target ≤ {gate.value}"
        return GateOutcome(gate, passed, observed, reason)

    if gate.op not in _OPS:
        return GateOutcome(gate, False, 0.0, f"unknown op: {gate.op!r}")
    if not gate.metric:
        return GateOutcome(gate, False, 0.0, f"gate {gate.name!r} missing 'metric'")

    cmp_fn, sym = _OPS[gate.op]
    observed = _agg_value(results, gate.metric)
    passed = cmp_fn(observed, gate.value)
    reason = f"{gate.metric} = {observed:.4f}; target {sym} {gate.value}"
    return GateOutcome(gate, passed, observed, reason)


def run_gates(results: Results, thresholds: ThresholdsConfig) -> GateReport:
    return GateReport(outcomes=[_evaluate(results, g) for g in thresholds.gates])


def load_thresholds(path: str | Path) -> ThresholdsConfig:
    raw = yaml.safe_load(Path(path).read_text())
    rows: Sequence[dict] = raw.get("gates", [])
    gates = tuple(
        Gate(
            name=str(r["name"]),
            op=str(r["op"]),
            value=float(r["value"]),
            metric=r.get("metric"),
            slice_metric=r.get("slice_metric"),
        )
        for r in rows
    )
    return ThresholdsConfig(gates=gates)
