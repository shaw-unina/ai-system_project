"""Markdown report writers for Phase 7. Smoke runs prepend a [SMOKE] banner."""
from __future__ import annotations

from pathlib import Path

from misinfo.eval.decisions import (
    HEADLINE_SYSTEM,
    NO_ABSTAIN_SYSTEM,
    H1Decision,
    SubHypothesisResult,
    decide_h1,
)
from misinfo.eval.phase7 import (
    Phase7Cell,
    Phase7Runs,
    aggregate_seeds,
    cells_for,
    confidences_and_correct,
)
from misinfo.eval.reliability import reliability_bins, risk_coverage_curve

SMOKE_BANNER = (
    "> ⚠️ **[SMOKE — synthetic data, do not cite]** This report was produced "
    "from a synthetic dataset under MockBackend. It validates the Phase 7 "
    "harness end-to-end; the headline numbers are not research findings. "
    "Replace with a real-run report before publication.\n"
)


def _header(runs: Phase7Runs, title: str) -> list[str]:
    out = [f"# {title}", ""]
    if runs.config.smoke:
        out += [SMOKE_BANNER, ""]
    return out


def _verdict_row(r: SubHypothesisResult) -> str:
    return (
        f"| {r.name} | {r.verdict} | {r.point:.4f} | {r.threshold:.4f} | "
        f"{('%.4f' % r.p_value) if r.p_value is not None else '—'} | {r.detail} |"
    )


def render_h1a(runs: Phase7Runs, decision: H1Decision) -> str:
    lines = _header(runs, "H1.a — Vulnerability of the no-abstention baseline")
    lines += [
        f"**Decision:** {decision.h1a.verdict}",
        "",
        "Largest F1 drop across attack families (no-abstention system):",
        "",
        "| sub-hypothesis | verdict | point | threshold | p | note |",
        "|---|---|---|---|---|---|",
        _verdict_row(decision.h1a),
        "",
        "## Per-family F1 (no-abstention)",
        "",
        "| family | F1-macro |",
        "|---|---|",
    ]
    for fam in ("clean", "newswire", "tabloid", "social"):
        m = aggregate_seeds(cells_for(runs, system=NO_ABSTAIN_SYSTEM, condition=fam))
        lines.append(f"| {fam} | {m.get('f1_macro', 0.0):.4f} |")
    return "\n".join(lines) + "\n"


def render_h1b(runs: Phase7Runs, decision: H1Decision) -> str:
    lines = _header(runs, "H1.b — Abstention recovery (F1 retention ≥ 80%)")
    lines += [
        f"**Decision:** {decision.h1b.verdict}",
        "",
        "| sub-hypothesis | verdict | point | threshold | p | note |",
        "|---|---|---|---|---|---|",
        _verdict_row(decision.h1b),
        "",
        f"## Per-family F1 ({HEADLINE_SYSTEM})",
        "",
        "| family | F1-macro | retention | acc@cov0.7 |",
        "|---|---|---|---|",
    ]
    clean = aggregate_seeds(cells_for(runs, system=HEADLINE_SYSTEM, condition="clean"))
    f1_clean = clean.get("f1_macro", 0.0) or 1e-9
    for fam in ("clean", "newswire", "tabloid", "social"):
        m = aggregate_seeds(cells_for(runs, system=HEADLINE_SYSTEM, condition=fam))
        retention = m.get("f1_macro", 0.0) / f1_clean
        lines.append(
            f"| {fam} | {m.get('f1_macro', 0.0):.4f} | {retention:.3f} | "
            f"{m.get('accuracy_at_70_coverage', 0.0):.4f} |"
        )
    return "\n".join(lines) + "\n"


def render_h1c(runs: Phase7Runs, decision: H1Decision) -> str:
    lines = _header(runs, "H1.c — Calibration improvement under attack")
    lines += [
        f"**Decision:** {decision.h1c.verdict}",
        "",
        "| sub-hypothesis | verdict | point | threshold | p | note |",
        "|---|---|---|---|---|---|",
        _verdict_row(decision.h1c),
        "",
        "## ECE per attack family",
        "",
        f"| family | ECE ({NO_ABSTAIN_SYSTEM}) | ECE ({HEADLINE_SYSTEM}) | Δ |",
        "|---|---|---|---|",
    ]
    for fam in ("newswire", "tabloid", "social"):
        no = aggregate_seeds(cells_for(runs, system=NO_ABSTAIN_SYSTEM, condition=fam))
        yes = aggregate_seeds(cells_for(runs, system=HEADLINE_SYSTEM, condition=fam))
        d = no.get("ece", 0.0) - yes.get("ece", 0.0)
        lines.append(f"| {fam} | {no.get('ece', 0.0):.4f} | {yes.get('ece', 0.0):.4f} | {d:+.4f} |")
    return "\n".join(lines) + "\n"


def render_h1d(runs: Phase7Runs, decision: H1Decision) -> str:
    lines = _header(runs, "H1.d — Anti-trivial-abstention guard (rate ∈ [0.10, 0.50])")
    lines += [
        f"**Decision:** {decision.h1d.verdict}",
        "",
        "| sub-hypothesis | verdict | point | threshold | p | note |",
        "|---|---|---|---|---|---|",
        _verdict_row(decision.h1d),
        "",
        f"## Abstention rate per attack family ({HEADLINE_SYSTEM})",
        "",
        "| family | rate | in band [0.10, 0.50]? |",
        "|---|---|---|",
    ]
    for fam in ("newswire", "tabloid", "social"):
        m = aggregate_seeds(cells_for(runs, system=HEADLINE_SYSTEM, condition=fam))
        rate = m.get("abstention_rate", 0.0)
        in_band = "yes" if 0.10 <= rate <= 0.50 else "no"
        lines.append(f"| {fam} | {rate:.3f} | {in_band} |")
    return "\n".join(lines) + "\n"


def _flatten_confidences(cells: list[Phase7Cell]) -> tuple[list[float], list[bool]]:
    confs: list[float] = []
    correct: list[bool] = []
    for c in cells:
        cs, cr = confidences_and_correct(c)
        confs.extend(cs)
        correct.extend(cr)
    return confs, correct


def render_calibration(runs: Phase7Runs) -> str:
    lines = _header(runs, "Calibration — reliability diagrams")
    for system in runs.config.systems:
        lines.append(f"## {system}")
        lines.append("")
        lines.append("| bin | n | mean conf | accuracy | gap |")
        lines.append("|---|---|---|---|---|")
        confs, correct = _flatten_confidences(runs.by_system(system))
        bins = reliability_bins(confs, correct, n_bins=10)
        for b in bins:
            gap = b.accuracy - b.confidence
            lines.append(
                f"| [{b.lo:.2f}, {b.hi:.2f}] | {b.n} | {b.confidence:.3f} | "
                f"{b.accuracy:.3f} | {gap:+.3f} |"
            )
        lines.append("")
    return "\n".join(lines) + "\n"


def render_risk_coverage(runs: Phase7Runs) -> str:
    lines = _header(runs, "Risk–coverage curves")
    for system in runs.config.systems:
        lines.append(f"## {system}")
        lines.append("")
        confs, correct = _flatten_confidences(runs.by_system(system))
        curve = risk_coverage_curve(confs, correct)
        lines.append("| coverage | risk |")
        lines.append("|---|---|")
        # downsample to ~10 points
        step = max(1, len(curve) // 10)
        for cov, risk in curve[::step]:
            lines.append(f"| {cov:.3f} | {risk:.3f} |")
        lines.append("")
    return "\n".join(lines) + "\n"


def render_robustness(runs: Phase7Runs) -> str:
    lines = _header(runs, "Robustness — system × condition F1")
    lines.append("| system | clean | newswire | tabloid | social |")
    lines.append("|---|---|---|---|---|")
    for system in runs.config.systems:
        cells = []
        for cond in ("clean", "newswire", "tabloid", "social"):
            cells.append(aggregate_seeds(cells_for(runs, system=system, condition=cond)))
        row = " | ".join(f"{c.get('f1_macro', 0.0):.3f}" for c in cells)
        lines.append(f"| {system} | {row} |")
    return "\n".join(lines) + "\n"


def render_fairness(runs: Phase7Runs) -> str:
    lines = _header(runs, "Fairness — per-topic accuracy on clean condition")
    lines.append(f"System: {HEADLINE_SYSTEM}")
    lines.append("")
    lines.append("| topic | n | accuracy |")
    lines.append("|---|---|---|")
    cells = cells_for(runs, system=HEADLINE_SYSTEM, condition="clean")
    by_topic: dict[str, list[bool]] = {}
    for c in cells:
        for r in c.results.per_claim:
            topic = r.claim.split(" about ", 1)[-1] if " about " in r.claim else "?"
            by_topic.setdefault(topic, []).append(r.correct)
    for topic, correct_list in sorted(by_topic.items()):
        n = len(correct_list)
        acc = sum(correct_list) / n if n else 0.0
        lines.append(f"| {topic} | {n} | {acc:.3f} |")
    return "\n".join(lines) + "\n"


def render_error_decomposition(runs: Phase7Runs) -> str:
    lines = _header(runs, "Error decomposition — confusion summary on clean condition")
    lines.append(f"System: {HEADLINE_SYSTEM}")
    lines.append("")
    lines.append("| gold \\ pred | Supported | Refuted | NotEnoughEvidence | Abstain |")
    lines.append("|---|---|---|---|---|")
    cells = cells_for(runs, system=HEADLINE_SYSTEM, condition="clean")
    cm: dict[tuple[str, str], int] = {}
    for c in cells:
        for r in c.results.per_claim:
            cm[(r.gold_label, r.verdict.verdict)] = cm.get((r.gold_label, r.verdict.verdict), 0) + 1
    for gold in ("Supported", "Refuted", "NotEnoughEvidence"):
        row = [str(cm.get((gold, p), 0)) for p in ("Supported", "Refuted", "NotEnoughEvidence", "Abstain")]
        lines.append(f"| {gold} | " + " | ".join(row) + " |")
    return "\n".join(lines) + "\n"


def render_averitec_score(runs: Phase7Runs) -> str:
    lines = _header(runs, "AVeriTeC recall proxy")
    lines += [
        "> Note: this is a recall-style proxy, not the official Ev2R score "
        "(which requires reference QA pairs we don't have). Documented in "
        "[src/misinfo/eval/metrics.py](../src/misinfo/eval/metrics.py).",
        "",
        "| system | clean | newswire | tabloid | social |",
        "|---|---|---|---|---|",
    ]
    for system in runs.config.systems:
        cells = [aggregate_seeds(cells_for(runs, system=system, condition=c))
                 for c in ("clean", "newswire", "tabloid", "social")]
        row = " | ".join(f"{c.get('averitec_recall_proxy', 0.0):.3f}" for c in cells)
        lines.append(f"| {system} | {row} |")
    return "\n".join(lines) + "\n"


REPORT_FILES = (
    ("h1a.md", "h1a"),
    ("h1b.md", "h1b"),
    ("h1c.md", "h1c"),
    ("h1d.md", "h1d"),
    ("calibration.md", "calibration"),
    ("risk-coverage.md", "risk_coverage"),
    ("robustness.md", "robustness"),
    ("fairness.md", "fairness"),
    ("error-decomposition.md", "error_decomposition"),
    ("averitec-score.md", "averitec_score"),
)


def write_all_reports(runs: Phase7Runs, out_dir: str | Path) -> dict[str, Path]:
    """Render every Phase 7 report into `out_dir`. Returns a name→path map."""
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)
    decision = decide_h1(runs)

    written: dict[str, Path] = {}
    payloads = {
        "h1a": render_h1a(runs, decision),
        "h1b": render_h1b(runs, decision),
        "h1c": render_h1c(runs, decision),
        "h1d": render_h1d(runs, decision),
        "calibration": render_calibration(runs),
        "risk_coverage": render_risk_coverage(runs),
        "robustness": render_robustness(runs),
        "fairness": render_fairness(runs),
        "error_decomposition": render_error_decomposition(runs),
        "averitec_score": render_averitec_score(runs),
    }
    for filename, key in REPORT_FILES:
        p = out / filename
        p.write_text(payloads[key])
        written[key] = p

    # Top-level decision summary
    summary = [
        "# Phase 7 — H1 decision summary",
        "",
        SMOKE_BANNER if runs.config.smoke else "",
        f"**Overall:** {decision.overall}",
        "",
        "| sub-hypothesis | verdict | point | threshold |",
        "|---|---|---|---|",
        f"| H1.a | {decision.h1a.verdict} | {decision.h1a.point:.4f} | {decision.h1a.threshold:.4f} |",
        f"| H1.b | {decision.h1b.verdict} | {decision.h1b.point:.4f} | {decision.h1b.threshold:.4f} |",
        f"| H1.c | {decision.h1c.verdict} | {decision.h1c.point:.4f} | {decision.h1c.threshold:.4f} |",
        f"| H1.d | {decision.h1d.verdict} | {decision.h1d.point:.4f} | {decision.h1d.threshold:.4f} |",
    ]
    p = out / "h1_decision.md"
    p.write_text("\n".join(summary) + "\n")
    written["h1_decision"] = p
    return written
