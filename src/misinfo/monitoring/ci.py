"""Tiny CI orchestrator — runs the regression eval + gate, exits non-zero on fail."""
from __future__ import annotations

import json
from pathlib import Path

from misinfo.eval.harness import run_eval
from misinfo.eval.results import Results
from misinfo.monitoring.gates import (
    GateReport,
    load_thresholds,
    run_gates,
)


def load_results(path: str | Path) -> Results:
    return Results.model_validate_json(Path(path).read_text())


def evaluate_results(results_path: Path, thresholds_path: Path) -> GateReport:
    results = load_results(results_path)
    thresholds = load_thresholds(thresholds_path)
    return run_gates(results, thresholds)


def regression_run(factchecker, dataset_path: Path) -> Results:
    rows = []
    with dataset_path.open("r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                rows.append(json.loads(line))
    return run_eval(factchecker, rows, system="regression", dataset_name=dataset_path.stem)
