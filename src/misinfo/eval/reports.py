"""Markdown report writer for an eval Results object."""
from __future__ import annotations

from pathlib import Path

from misinfo.eval.results import Results


def render_markdown(r: Results) -> str:
    a = r.aggregate
    lines = [
        f"# Eval report — {r.system} on {r.dataset}",
        "",
        f"- generated: {r.generated_at_utc}",
        f"- n_claims: {r.n_claims}",
        "",
        "## Aggregate metrics",
        "",
        "| metric | value |",
        "|---|---|",
        f"| accuracy | {a.accuracy:.4f} |",
        f"| f1_macro | {a.f1_macro:.4f} |",
        f"| ECE | {a.ece:.4f} |",
        f"| MCE | {a.mce:.4f} |",
        f"| AURC | {a.aurc:.4f} |",
        f"| accuracy @ 0.7 cov | {a.accuracy_at_70_coverage:.4f} |",
        f"| averitec_recall_proxy | {a.averitec_recall_proxy:.4f} |",
        f"| abstention_rate | {a.abstention_rate:.4f} |",
    ]
    if r.slices:
        lines += ["", "## Slices", "", "| slice | n | acc | macro-F1 | ECE | abstain |", "|---|---|---|---|---|---|"]
        for s in r.slices:
            m = s.metrics
            lines.append(
                f"| {s.name} | {s.n} | {m.accuracy:.3f} | {m.f1_macro:.3f} | {m.ece:.3f} | {m.abstention_rate:.3f} |"
            )
    return "\n".join(lines) + "\n"


def write_report(r: Results, path: str | Path) -> Path:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(render_markdown(r))
    return p
