from misinfo.monitoring.drift import (
    drift_report,
    psi,
    snapshot_categorical,
    snapshot_numeric,
)
from misinfo.monitoring.snapshot import load_snapshots, save_snapshots


def test_psi_zero_on_identical_categorical():
    a = snapshot_categorical(["x", "y", "x", "y", "x"], name="v")
    b = snapshot_categorical(["x", "y", "x", "y", "x"], name="v")
    assert psi(a, b) == 0.0


def test_psi_large_on_disjoint():
    a = snapshot_categorical(["x"] * 100, name="v")
    b = snapshot_categorical(["y"] * 100, name="v")
    assert psi(a, b) > 1.0  # well into "major" territory


def test_psi_numeric_zero_on_identical():
    edges = [0.0, 0.5, 1.0001]
    a = snapshot_numeric([0.1, 0.2, 0.6, 0.9], name="c", edges=edges)
    b = snapshot_numeric([0.1, 0.2, 0.6, 0.9], name="c", edges=edges)
    assert psi(a, b) == 0.0


def test_drift_report_overall_is_worst():
    a1 = snapshot_categorical(["x", "y"], name="a")
    a2 = snapshot_categorical(["x", "y"], name="a")
    b1 = snapshot_categorical(["p"] * 50, name="b")
    b2 = snapshot_categorical(["q"] * 50, name="b")
    report = drift_report([a1, b1], [a2, b2])
    assert report.overall == "major"
    assert report.verdict_by_feature["a"] == "stable"
    assert report.verdict_by_feature["b"] == "major"


def test_snapshot_roundtrip_json(tmp_path):
    snaps = [
        snapshot_categorical(["x", "y", "x"], name="v"),
        snapshot_numeric([0.1, 0.5, 0.9], name="c", edges=[0.0, 0.5, 1.0001]),
    ]
    p = tmp_path / "snap.json"
    save_snapshots(snaps, p)
    loaded = load_snapshots(p)
    assert len(loaded) == 2
    assert loaded[0].name == "v"
    assert loaded[1].kind == "numeric"
