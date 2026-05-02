"""Phase 7 orchestrator: systems × conditions × seeds → per-cell Results.

The smoke path uses synthetic claims + MockBackend so CI can exercise the
full pipeline end-to-end. The real-run path consumes Phase 3 artefacts
(AVeriTeC dev + the LLM-paraphrase attack set) and is documented in
[docs/phase-7-evaluation.md](docs/phase-7-evaluation.md). Only the smoke path
is tested.
"""
from __future__ import annotations

import json
from collections.abc import Sequence
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import numpy as np

from misinfo.abstention.base import CalibrationRecord
from misinfo.abstention.registry import head_class
from misinfo.abstention.threshold import select_threshold_for_coverage
from misinfo.decompose.llm_decomposer import LLMDecomposer
from misinfo.eval.folds import ThreeWayFolds, select, three_way_split
from misinfo.eval.harness import run_eval
from misinfo.eval.results import Results
from misinfo.inference.base import LanguageModel
from misinfo.inference.mock_backend import MockBackend
from misinfo.pipeline.orchestrator import RAGFactChecker
from misinfo.retrieve.bm25 import BM25Retriever
from misinfo.retrieve.corpus import EvidenceCorpus
from misinfo.schemas import AggregatorOutput, QuestionAnswer, SubQuestion
from misinfo.verify.aggregator import LLMAggregator
from misinfo.verify.answerer import LLMAnswerer

DEFAULT_SYSTEMS = (
    "rag_identity",
    "rag_temperature",
    "rag_isotonic",
    "rag_retrieval_gated",
    "rag_fusion",
)
DEFAULT_CONDITIONS = ("clean", "newswire", "tabloid", "social")


@dataclass
class Phase7Config:
    systems: list[str] = field(default_factory=lambda: list(DEFAULT_SYSTEMS))
    conditions: list[str] = field(default_factory=lambda: list(DEFAULT_CONDITIONS))
    seeds: list[int] = field(default_factory=lambda: [1, 2, 3])
    target_coverage: float = 0.7
    out_dir: Path = Path("reports/phase7")
    smoke: bool = False
    limit: int | None = None


@dataclass
class Phase7Cell:
    system: str
    condition: str
    seed: int
    results: Results

    @property
    def key(self) -> str:
        return f"{self.system}__{self.condition}__seed{self.seed}"


@dataclass
class Phase7Runs:
    config: Phase7Config
    cells: list[Phase7Cell]
    tau_by_system: dict[str, float]

    def by_condition(self, condition: str) -> list[Phase7Cell]:
        return [c for c in self.cells if c.condition == condition]

    def by_system(self, system: str) -> list[Phase7Cell]:
        return [c for c in self.cells if c.system == system]

    def find(self, system: str, condition: str, seed: int) -> Phase7Cell | None:
        for c in self.cells:
            if c.system == system and c.condition == condition and c.seed == seed:
                return c
        return None


# ---------------------------------------------------------------------------
# Synthetic data generation for the smoke path
# ---------------------------------------------------------------------------

_LABELS = ("Supported", "Refuted", "NotEnoughEvidence")


def make_synthetic_dataset(n: int, *, seed: int) -> list[dict[str, Any]]:
    rng = np.random.default_rng(seed)
    rows = []
    for i in range(n):
        label = _LABELS[int(rng.integers(0, 3))]
        topic = ["politics", "health", "climate"][int(rng.integers(0, 3))]
        rows.append({
            "claim_id": f"syn-{seed}-{i:04d}",
            "claim": f"synthetic claim {i} about {topic}",
            "label": label,
            "topic": topic,
        })
    return rows


def make_synthetic_attack(rows: list[dict[str, Any]], style: str) -> list[dict[str, Any]]:
    return [{**r, "claim_id": f"{r['claim_id']}-{style}",
             "claim": f"[{style}] {r['claim']}", "style": style} for r in rows]


def _scripted_factory(seed: int):
    """Returns a MockBackend response_factory that produces seeded structured
    outputs across all stages, biased so the system is right ~60% of the time —
    enough signal that the report writers see non-degenerate numbers."""
    rng = np.random.default_rng(seed)

    # Ensure the prompt namespace import doesn't clash. We import lazily
    # because _DecomposerOutput is a private symbol of the decomposer module.
    from misinfo.decompose.llm_decomposer import _DecomposerOutput

    def factory(prompt: str, schema: type):
        if schema is _DecomposerOutput:
            return _DecomposerOutput(questions=[SubQuestion(question="q?")])
        if schema is QuestionAnswer:
            return QuestionAnswer(question="q", answer="a", evidence=[])
        if schema is AggregatorOutput:
            label = _LABELS[int(rng.integers(0, 3))]
            return AggregatorOutput(
                verdict=label,  # type: ignore[arg-type]
                confidence=float(rng.uniform(0.3, 0.95)),
                rationale="synthetic rationale",
                evidence=[],
            )
        return schema()  # type: ignore[call-arg]

    return factory


# ---------------------------------------------------------------------------
# System builders
# ---------------------------------------------------------------------------

def _build_rag(llm: LanguageModel, head_name: str, *, head=None, tau=None) -> RAGFactChecker:
    return RAGFactChecker(
        decomposer=LLMDecomposer(llm),
        retriever=BM25Retriever(EvidenceCorpus()),
        answerer=LLMAnswerer(llm),
        aggregator=LLMAggregator(llm),
        abstention=head,
        backend_id="mock",
        model_id=llm.model_id,
        abstain_threshold=tau,
    )


def build_system(name: str, llm: LanguageModel, *, head=None, tau=None):
    if not name.startswith("rag_"):
        raise ValueError(f"unknown system: {name!r}")
    head_name = name.removeprefix("rag_")
    if head is None and head_name != "identity":
        head = head_class(head_name)()
    return _build_rag(llm, head_name, head=head, tau=tau)


# ---------------------------------------------------------------------------
# Calibration: one-pass eval on the calibration fold to produce records
# ---------------------------------------------------------------------------

def _records_from_results(results: Results) -> list[CalibrationRecord]:
    out = []
    for r in results.per_claim:
        out.append(CalibrationRecord(
            verifier_confidence=float(r.verdict.confidence),
            mean_top1=float(r.signals.get("mean_top1", 0.0)),
            evidence_coverage=float(r.signals.get("evidence_coverage", 0.0)),
            correct=bool(r.correct),
        ))
    return out


def _calibrate_head(name: str, llm: LanguageModel, calibration_rows: list[dict[str, Any]]):
    """Fit the named head on calibration rows. Returns (head, fitted_or_None)."""
    head_name = name.removeprefix("rag_")
    if head_name == "identity":
        return None
    cls = head_class(head_name)
    head = cls()
    fc = _build_rag(llm, head_name, head=None, tau=None)
    cal_results = run_eval(fc, calibration_rows, system=name, dataset_name="calibration")
    head.fit(_records_from_results(cal_results))
    return head


def _select_tau(fc, threshold_rows: list[dict[str, Any]], target_coverage: float) -> float:
    res = run_eval(fc, threshold_rows, system="threshold", dataset_name="threshold")
    confs = [c.verdict.confidence for c in res.per_claim]
    return select_threshold_for_coverage(confs, target_coverage)


# ---------------------------------------------------------------------------
# Top-level orchestration
# ---------------------------------------------------------------------------

def run_phase7(config: Phase7Config) -> Phase7Runs:
    if not config.smoke:
        raise NotImplementedError(
            "Real Phase 7 run is documented in docs/phase-7-evaluation.md; "
            "only --smoke is implemented in code per the approved Phase 7 plan."
        )

    out_dir = Path(config.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Build deterministic synthetic data
    n_claims = config.limit or 60
    base_rows = make_synthetic_dataset(n_claims, seed=0)
    folds: ThreeWayFolds = three_way_split(len(base_rows))

    cal_rows = select(base_rows, folds.calibration)
    thr_rows = select(base_rows, folds.threshold)
    eval_rows = select(base_rows, folds.eval)

    # One LLM per seed, scripted so reports show non-degenerate signal
    cells: list[Phase7Cell] = []
    tau_by_system: dict[str, float] = {}

    for system in config.systems:
        # Calibrate head on calibration fold (using a fixed factory seed so
        # the calibration LLM is deterministic across systems).
        cal_llm = MockBackend(response_factory=_scripted_factory(seed=10_000))
        head = _calibrate_head(system, cal_llm, cal_rows)

        # Pick τ on threshold fold using the calibrated head
        thr_llm = MockBackend(response_factory=_scripted_factory(seed=20_000))
        thr_fc = build_system(system, thr_llm, head=head, tau=None)
        tau = _select_tau(thr_fc, thr_rows, config.target_coverage)
        tau_by_system[system] = tau

        for condition in config.conditions:
            condition_rows = (
                eval_rows if condition == "clean"
                else make_synthetic_attack(eval_rows, condition)
            )
            for seed in config.seeds:
                llm = MockBackend(response_factory=_scripted_factory(seed=seed * 1000))
                fc = build_system(system, llm, head=head, tau=tau)
                results = run_eval(
                    fc, condition_rows,
                    system=system, dataset_name=condition,
                )
                cell = Phase7Cell(system=system, condition=condition, seed=seed, results=results)
                cells.append(cell)
                cell_path = out_dir / "cells" / f"{cell.key}.json"
                cell_path.parent.mkdir(parents=True, exist_ok=True)
                cell_path.write_text(results.model_dump_json(indent=2))

    runs = Phase7Runs(config=config, cells=cells, tau_by_system=tau_by_system)
    _write_summary_csv(runs, out_dir / "phase7_runs.csv")
    return runs


def _write_summary_csv(runs: Phase7Runs, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    rows = ["system,condition,seed,n,accuracy,f1_macro,ece,aurc,abstention_rate,tau"]
    for c in runs.cells:
        a = c.results.aggregate
        rows.append(
            f"{c.system},{c.condition},{c.seed},{a.n},{a.accuracy:.6f},{a.f1_macro:.6f},"
            f"{a.ece:.6f},{a.aurc:.6f},{a.abstention_rate:.6f},"
            f"{runs.tau_by_system.get(c.system, 0.0):.6f}"
        )
    path.write_text("\n".join(rows) + "\n")


def write_runs_metadata(runs: Phase7Runs, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    meta = {
        "systems": runs.config.systems,
        "conditions": runs.config.conditions,
        "seeds": runs.config.seeds,
        "target_coverage": runs.config.target_coverage,
        "smoke": runs.config.smoke,
        "tau_by_system": runs.tau_by_system,
    }
    path.write_text(json.dumps(meta, indent=2))


def cells_for(runs: Phase7Runs, *, system: str, condition: str) -> list[Phase7Cell]:
    return [c for c in runs.cells if c.system == system and c.condition == condition]


def labels_and_preds(cell: Phase7Cell) -> tuple[list[str], list[str]]:
    y_true = [r.gold_label for r in cell.results.per_claim]
    y_pred = [r.verdict.verdict for r in cell.results.per_claim]
    return y_true, y_pred


def confidences_and_correct(cell: Phase7Cell) -> tuple[list[float], list[bool]]:
    confs = [r.verdict.confidence for r in cell.results.per_claim]
    correct = [r.correct for r in cell.results.per_claim]
    return confs, correct


def aggregate_seeds(cells: Sequence[Phase7Cell]) -> dict[str, float]:
    """Mean over seeds for the headline aggregate metrics."""
    if not cells:
        return {}
    keys = ("accuracy", "f1_macro", "ece", "mce", "aurc",
            "accuracy_at_70_coverage", "averitec_recall_proxy", "abstention_rate")
    out = {}
    for k in keys:
        vals = [getattr(c.results.aggregate, k) for c in cells]
        out[k] = float(sum(vals) / len(vals))
    return out
