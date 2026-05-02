import json
import pathlib

from misinfo import cli
from misinfo.eval.harness import run_eval
from misinfo.monitoring.drift import snapshots_from_results
from misinfo.monitoring.snapshot import save_snapshots
from tests.conftest_api import build_mock_factchecker

REPO = pathlib.Path(__file__).resolve().parents[1]
DATA = REPO / "tests" / "data" / "regression_frozen.jsonl"
THRESHOLDS = REPO / "docs" / "phase-9" / "thresholds.example.yaml"


def _make_results(tmp_path):
    fc = build_mock_factchecker()
    rows = [json.loads(l) for l in DATA.read_text().splitlines() if l.strip()]
    results = run_eval(fc, rows, system="t", dataset_name="t")
    p = tmp_path / "results.json"
    p.write_text(results.model_dump_json())
    return p, results


def test_cli_gate_passes_on_thresholds(tmp_path, capsys):
    results_path, _ = _make_results(tmp_path)
    rc = cli.main([
        "gate",
        "--results", str(results_path),
        "--thresholds", str(THRESHOLDS),
        "--report", str(tmp_path / "gate.md"),
    ])
    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["passed"] is True
    assert (tmp_path / "gate.md").exists()


def test_cli_gate_fails_on_breach(tmp_path, capsys):
    results_path, _ = _make_results(tmp_path)
    th = tmp_path / "th.yaml"
    th.write_text("gates:\n  - name: impossible\n    metric: accuracy\n    op: ge\n    value: 1.5\n")
    rc = cli.main(["gate", "--results", str(results_path), "--thresholds", str(th)])
    assert rc == 1


def test_cli_monitor_drift_identical_snapshots(tmp_path, capsys):
    _, results = _make_results(tmp_path)
    snaps = snapshots_from_results(results)
    a = tmp_path / "a.json"
    save_snapshots(snaps, a)
    rc = cli.main([
        "monitor", "drift",
        "--reference", str(a),
        "--live", str(a),
        "--report", str(tmp_path / "drift.md"),
    ])
    assert rc == 0
    payload = json.loads(capsys.readouterr().out)
    assert payload["overall"] == "stable"
    for v in payload["psi"].values():
        assert v == 0.0


def test_cli_monitor_snapshot_roundtrip(tmp_path):
    results_path, _ = _make_results(tmp_path)
    out = tmp_path / "snap.json"
    rc = cli.main([
        "monitor", "snapshot",
        "--input", str(results_path),
        "--output", str(out),
    ])
    assert rc == 0
    assert out.exists()
    payload = json.loads(out.read_text())
    names = [s["name"] for s in payload]
    assert "verdict" in names and "confidence" in names
