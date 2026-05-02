"""Frozen-set regression: a synthetic 30-claim eval that must not drift.

Drift on this number = unintended pipeline change. Real drift detection lights
up only against a real reference snapshot taken at release time.
"""
from __future__ import annotations

import pathlib

from misinfo.monitoring.ci import regression_run
from misinfo.monitoring.gates import load_thresholds, run_gates
from tests.conftest_api import build_mock_factchecker

REPO = pathlib.Path(__file__).resolve().parents[1]
DATA = REPO / "tests" / "data" / "regression_frozen.jsonl"
THRESHOLDS = REPO / "docs" / "phase-9" / "thresholds.example.yaml"


def test_regression_set_passes_thresholds():
    fc = build_mock_factchecker()
    results = regression_run(fc, DATA)
    assert results.n_claims == 30

    thresholds = load_thresholds(THRESHOLDS)
    report = run_gates(results, thresholds)
    breached = [o.gate.name for o in report.outcomes if not o.passed]
    assert report.passed, f"gates breached: {breached}"
