"""End-to-end smoke for the Phase 7 harness on synthetic data + MockBackend."""
from __future__ import annotations

from misinfo.eval.decisions import decide_h1
from misinfo.eval.phase7 import Phase7Config, run_phase7
from misinfo.eval.reports_phase7 import REPORT_FILES, write_all_reports


def test_phase7_smoke_renders_all_reports(tmp_path):
    cfg = Phase7Config(
        systems=["rag_identity", "rag_fusion"],
        conditions=["clean", "newswire", "tabloid", "social"],
        seeds=[1, 2],
        out_dir=tmp_path,
        smoke=True,
        limit=60,
    )
    runs = run_phase7(cfg)
    # systems × conditions × seeds = 2 × 4 × 2 = 16 cells
    assert len(runs.cells) == 16
    # Every system has a τ
    assert set(runs.tau_by_system) == set(cfg.systems)

    written = write_all_reports(runs, tmp_path)
    for filename, _ in REPORT_FILES:
        assert (tmp_path / filename).exists()
        assert (tmp_path / filename).read_text().startswith("# ")
    assert "h1_decision" in written

    decision = decide_h1(runs)
    for sub in (decision.h1a, decision.h1b, decision.h1c, decision.h1d):
        assert sub.verdict in ("supported", "rejected", "inconclusive")


def test_phase7_smoke_summary_csv(tmp_path):
    cfg = Phase7Config(
        systems=["rag_identity"],
        conditions=["clean", "newswire"],
        seeds=[1],
        out_dir=tmp_path,
        smoke=True,
        limit=40,
    )
    run_phase7(cfg)
    csv = (tmp_path / "phase7_runs.csv").read_text()
    lines = csv.strip().split("\n")
    assert lines[0].startswith("system,condition,seed,")
    assert len(lines) == 1 + 1 * 2 * 1  # header + cells


def test_phase7_real_run_not_implemented(tmp_path):
    import pytest
    cfg = Phase7Config(out_dir=tmp_path, smoke=False, limit=10)
    with pytest.raises(NotImplementedError):
        run_phase7(cfg)
