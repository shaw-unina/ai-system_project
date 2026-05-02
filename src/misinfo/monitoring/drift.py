"""Drift detection — Population Stability Index over distribution snapshots.

Snapshot semantics:
- Categorical: bins are the distinct values; counts are occurrences.
- Numeric: bins are `[edges[i], edges[i+1])`; the last bin is closed on the right.

PSI semantics:
    PSI = Σ (live% − ref%) · ln(live% / ref%)
    < 0.10  → "stable"
    < 0.25  → "minor"
    ≥ 0.25  → "major"
"""
from __future__ import annotations

import math
from collections import Counter
from collections.abc import Iterable, Sequence
from dataclasses import dataclass, field
from typing import Literal

DriftVerdict = Literal["stable", "minor", "major"]
PSI_MINOR = 0.10
PSI_MAJOR = 0.25


@dataclass(frozen=True)
class DistributionSnapshot:
    name: str
    bins: tuple[str, ...]
    counts: tuple[int, ...]
    n: int
    kind: Literal["categorical", "numeric"] = "categorical"
    edges: tuple[float, ...] | None = None

    def to_dict(self) -> dict:
        return {
            "name": self.name,
            "bins": list(self.bins),
            "counts": list(self.counts),
            "n": self.n,
            "kind": self.kind,
            "edges": list(self.edges) if self.edges is not None else None,
        }

    @classmethod
    def from_dict(cls, d: dict) -> "DistributionSnapshot":
        edges = d.get("edges")
        return cls(
            name=str(d["name"]),
            bins=tuple(str(b) for b in d["bins"]),
            counts=tuple(int(c) for c in d["counts"]),
            n=int(d["n"]),
            kind=d.get("kind", "categorical"),
            edges=tuple(float(e) for e in edges) if edges else None,
        )


def snapshot_categorical(values: Iterable[str], *, name: str) -> DistributionSnapshot:
    counter = Counter(str(v) for v in values)
    bins = tuple(sorted(counter))
    counts = tuple(counter[b] for b in bins)
    return DistributionSnapshot(name=name, bins=bins, counts=counts, n=sum(counts))


def snapshot_numeric(
    values: Iterable[float],
    *,
    name: str,
    edges: Sequence[float],
) -> DistributionSnapshot:
    edge_list = [float(e) for e in edges]
    if len(edge_list) < 2:
        raise ValueError("edges must have at least two entries")
    counts = [0] * (len(edge_list) - 1)
    n = 0
    for v in values:
        n += 1
        x = float(v)
        # Last bin is closed on the right
        for i in range(len(edge_list) - 1):
            lo, hi = edge_list[i], edge_list[i + 1]
            in_bin = (lo <= x < hi) if i < len(edge_list) - 2 else (lo <= x <= hi)
            if in_bin:
                counts[i] += 1
                break
    bins = tuple(f"[{edge_list[i]:.3g},{edge_list[i+1]:.3g})" for i in range(len(edge_list) - 1))
    return DistributionSnapshot(
        name=name,
        bins=bins,
        counts=tuple(counts),
        n=n,
        kind="numeric",
        edges=tuple(edge_list),
    )


def psi(
    reference: DistributionSnapshot,
    live: DistributionSnapshot,
    *,
    eps: float = 1e-4,
) -> float:
    if reference.bins != live.bins:
        # Re-bin live onto reference's bins; missing bins → 0 count.
        ref_keys = list(reference.bins)
        live_map = dict(zip(live.bins, live.counts, strict=True))
        ref_counts = list(reference.counts)
        live_counts = [live_map.get(k, 0) for k in ref_keys]
    else:
        ref_counts = list(reference.counts)
        live_counts = list(live.counts)
    n_ref = max(1, sum(ref_counts))
    n_live = max(1, sum(live_counts))
    total = 0.0
    for r, l in zip(ref_counts, live_counts, strict=True):
        p_ref = max(eps, r / n_ref)
        p_live = max(eps, l / n_live)
        total += (p_live - p_ref) * math.log(p_live / p_ref)
    return float(total)


def _classify(value: float) -> DriftVerdict:
    if value < PSI_MINOR:
        return "stable"
    if value < PSI_MAJOR:
        return "minor"
    return "major"


@dataclass(frozen=True)
class DriftReport:
    psi_by_feature: dict[str, float]
    verdict_by_feature: dict[str, DriftVerdict]
    overall: DriftVerdict
    notes: list[str] = field(default_factory=list)


def drift_report(
    reference: list[DistributionSnapshot],
    live: list[DistributionSnapshot],
) -> DriftReport:
    ref_by_name = {s.name: s for s in reference}
    psi_by: dict[str, float] = {}
    verdict_by: dict[str, DriftVerdict] = {}
    notes: list[str] = []
    for s in live:
        if s.name not in ref_by_name:
            notes.append(f"feature {s.name!r} not in reference — skipped")
            continue
        v = psi(ref_by_name[s.name], s)
        psi_by[s.name] = v
        verdict_by[s.name] = _classify(v)
    overall: DriftVerdict = "stable"
    for v in verdict_by.values():
        if v == "major":
            overall = "major"
            break
        if v == "minor":
            overall = "minor"
    return DriftReport(psi_by, verdict_by, overall, notes)


_CONFIDENCE_EDGES = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0001]
_CLAIM_LEN_EDGES = [0.0, 50.0, 100.0, 250.0, 500.0, 1000.0, 2000.0, 4000.0, float("inf")]


def snapshots_from_results(results) -> list[DistributionSnapshot]:
    """Build the canonical four snapshots from an `eval.results.Results` object."""
    verdicts = [r.verdict.verdict for r in results.per_claim]
    confidences = [r.verdict.confidence for r in results.per_claim]
    lengths = [len(r.claim) for r in results.per_claim]
    abstains = ["abstain" if r.verdict.verdict == "Abstain" else "not_abstain"
                for r in results.per_claim]
    return [
        snapshot_categorical(verdicts, name="verdict"),
        snapshot_numeric(confidences, name="confidence", edges=_CONFIDENCE_EDGES),
        snapshot_numeric(lengths, name="claim_length", edges=_CLAIM_LEN_EDGES),
        snapshot_categorical(abstains, name="abstain"),
    ]


def render_drift_markdown(report: DriftReport) -> str:
    lines = ["# Drift report", "", f"**Overall:** {report.overall}", ""]
    lines += ["| feature | PSI | verdict |", "|---|---|---|"]
    for feature, value in sorted(report.psi_by_feature.items()):
        lines.append(f"| {feature} | {value:.4f} | {report.verdict_by_feature[feature]} |")
    if report.notes:
        lines += ["", "## Notes", ""]
        for n in report.notes:
            lines.append(f"- {n}")
    return "\n".join(lines) + "\n"
