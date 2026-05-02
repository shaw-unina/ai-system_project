"""H1.a–d decision logic. Each `decide_*` returns a structured verdict the
report writers serialise into markdown."""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

from misinfo.eval import metrics as M
from misinfo.eval.bootstrap import paired_bootstrap_diff
from misinfo.eval.phase7 import (
    Phase7Cell,
    Phase7Runs,
    cells_for,
    labels_and_preds,
)

Verdict = Literal["supported", "rejected", "inconclusive"]
ATTACK_FAMILIES = ("newswire", "tabloid", "social")
HEADLINE_SYSTEM = "rag_fusion"
NO_ABSTAIN_SYSTEM = "rag_identity"


@dataclass
class SubHypothesisResult:
    name: str
    verdict: Verdict
    point: float
    threshold: float
    p_value: float | None = None
    detail: str = ""


@dataclass
class H1Decision:
    h1a: SubHypothesisResult
    h1b: SubHypothesisResult
    h1c: SubHypothesisResult
    h1d: SubHypothesisResult
    overall: Verdict = "inconclusive"
    notes: list[str] = field(default_factory=list)


def _avg_f1(cells: list[Phase7Cell]) -> float:
    if not cells:
        return 0.0
    vals = [c.results.aggregate.f1_macro for c in cells]
    return sum(vals) / len(vals)


def _avg_ece(cells: list[Phase7Cell]) -> float:
    if not cells:
        return 0.0
    return sum(c.results.aggregate.ece for c in cells) / len(cells)


def _avg_abstain(cells: list[Phase7Cell]) -> float:
    if not cells:
        return 0.0
    return sum(c.results.aggregate.abstention_rate for c in cells) / len(cells)


def decide_h1a(runs: Phase7Runs, *, n_bootstrap: int = 1000) -> SubHypothesisResult:
    """H1.a: without abstention, F1 drop ≥ 15 abs pts on at least one attack family."""
    clean_cells = cells_for(runs, system=NO_ABSTAIN_SYSTEM, condition="clean")
    f1_clean = _avg_f1(clean_cells)
    biggest_drop = 0.0
    biggest_p = 1.0
    family = ""
    for fam in ATTACK_FAMILIES:
        atk_cells = cells_for(runs, system=NO_ABSTAIN_SYSTEM, condition=fam)
        f1_atk = _avg_f1(atk_cells)
        drop = f1_clean - f1_atk
        if drop > biggest_drop:
            biggest_drop = drop
            family = fam
            if clean_cells and atk_cells:
                # Paired bootstrap on F1(clean) - F1(atk) for the first seed only
                yt_c, yp_c = labels_and_preds(clean_cells[0])
                yt_a, yp_a = labels_and_preds(atk_cells[0])
                # Pad to common length (synthetic) — paired requires same n
                m = min(len(yt_c), len(yt_a))
                if m:
                    res = paired_bootstrap_diff(
                        M.f1_macro, yt_c[:m], yp_c[:m], yp_a[:m],
                        n=n_bootstrap, seed=42,
                    )
                    biggest_p = float(res.p_value)
    threshold = 0.15
    verdict: Verdict = "supported" if biggest_drop >= threshold and biggest_p <= 0.05 else "rejected"
    return SubHypothesisResult(
        name="H1.a",
        verdict=verdict,
        point=biggest_drop * 100,  # express as abs pts
        threshold=threshold * 100,
        p_value=biggest_p,
        detail=f"largest F1 drop on {family or '(no attack family yet)'}",
    )


def decide_h1b(runs: Phase7Runs) -> SubHypothesisResult:
    """H1.b: with abstention, F1 retention ≥ 80% across all attack families."""
    clean_cells = cells_for(runs, system=HEADLINE_SYSTEM, condition="clean")
    f1_clean = _avg_f1(clean_cells)
    if f1_clean == 0:
        return SubHypothesisResult("H1.b", "inconclusive", 0.0, 0.80,
                                   detail="no clean F1 available")
    worst = 1.0
    family = ""
    for fam in ATTACK_FAMILIES:
        atk_cells = cells_for(runs, system=HEADLINE_SYSTEM, condition=fam)
        retention = _avg_f1(atk_cells) / f1_clean if f1_clean else 0.0
        if retention < worst:
            worst = retention
            family = fam
    verdict: Verdict = "supported" if worst >= 0.80 else "rejected"
    return SubHypothesisResult(
        name="H1.b",
        verdict=verdict,
        point=worst,
        threshold=0.80,
        detail=f"worst-case retention on {family}",
    )


def decide_h1c(runs: Phase7Runs) -> SubHypothesisResult:
    """H1.c: under attack, ECE(abstention) ≤ ECE(no-abstention)."""
    deltas = []
    for fam in ATTACK_FAMILIES:
        ece_no = _avg_ece(cells_for(runs, system=NO_ABSTAIN_SYSTEM, condition=fam))
        ece_yes = _avg_ece(cells_for(runs, system=HEADLINE_SYSTEM, condition=fam))
        deltas.append(ece_no - ece_yes)
    mean_delta = sum(deltas) / len(deltas) if deltas else 0.0
    verdict: Verdict = "supported" if mean_delta > 0 else "rejected"
    return SubHypothesisResult(
        name="H1.c",
        verdict=verdict,
        point=mean_delta,
        threshold=0.0,
        detail="mean ECE reduction across attack families",
    )


def decide_h1d(runs: Phase7Runs) -> SubHypothesisResult:
    """H1.d: abstention rate stays in [0.10, 0.50] per attack family."""
    bad = []
    rates = {}
    for fam in ATTACK_FAMILIES:
        rate = _avg_abstain(cells_for(runs, system=HEADLINE_SYSTEM, condition=fam))
        rates[fam] = rate
        if not (0.10 <= rate <= 0.50):
            bad.append(fam)
    verdict: Verdict = "rejected" if bad else "supported"
    point = max(abs(r - 0.30) for r in rates.values()) if rates else 0.0
    return SubHypothesisResult(
        name="H1.d",
        verdict=verdict,
        point=point,
        threshold=0.20,
        detail=("rates within band" if not bad else f"out of band: {bad}"),
    )


def decide_h1(runs: Phase7Runs) -> H1Decision:
    a = decide_h1a(runs)
    b = decide_h1b(runs)
    c = decide_h1c(runs)
    d = decide_h1d(runs)
    overall: Verdict = "supported" if all(
        x.verdict == "supported" for x in (a, b, c, d)
    ) else "rejected"
    return H1Decision(h1a=a, h1b=b, h1c=c, h1d=d, overall=overall)
