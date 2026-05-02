from misinfo.eval.results import AggregateMetrics, Results, SliceMetrics
from misinfo.monitoring.gates import (
    Gate,
    ThresholdsConfig,
    load_thresholds,
    run_gates,
)


def _agg(**overrides) -> AggregateMetrics:
    base = dict(
        n=10, accuracy=0.7, f1_macro=0.65, ece=0.1, mce=0.2, aurc=0.3,
        accuracy_at_70_coverage=0.75, averitec_recall_proxy=0.6,
        abstention_rate=0.2,
    )
    base.update(overrides)
    return AggregateMetrics(**base)


def _results(slices=None) -> Results:
    return Results(
        system="t", dataset="t", n_claims=10, aggregate=_agg(),
        slices=slices or [], per_claim=[],
    )


def test_ge_gate_passes_when_above():
    cfg = ThresholdsConfig(gates=(Gate(name="acc", op="ge", value=0.5, metric="accuracy"),))
    report = run_gates(_results(), cfg)
    assert report.passed
    assert report.outcomes[0].observed == 0.7


def test_le_gate_fails_when_above():
    cfg = ThresholdsConfig(gates=(Gate(name="ece", op="le", value=0.05, metric="ece"),))
    report = run_gates(_results(), cfg)
    assert not report.passed


def test_spread_le_gate_with_slices():
    slices = [
        SliceMetrics(name="politics", n=5, metrics=_agg(f1_macro=0.7)),
        SliceMetrics(name="health", n=5, metrics=_agg(f1_macro=0.5)),
    ]
    cfg = ThresholdsConfig(gates=(
        Gate(name="fair", op="spread_le", value=0.30, slice_metric="f1_macro"),
    ))
    report = run_gates(_results(slices=slices), cfg)
    assert report.passed
    assert abs(report.outcomes[0].observed - 0.20) < 1e-9


def test_spread_le_gate_breach():
    slices = [
        SliceMetrics(name="politics", n=5, metrics=_agg(f1_macro=0.9)),
        SliceMetrics(name="health", n=5, metrics=_agg(f1_macro=0.4)),
    ]
    cfg = ThresholdsConfig(gates=(
        Gate(name="fair", op="spread_le", value=0.20, slice_metric="f1_macro"),
    ))
    report = run_gates(_results(slices=slices), cfg)
    assert not report.passed


def test_load_thresholds_yaml(tmp_path):
    p = tmp_path / "th.yaml"
    p.write_text(
        "gates:\n"
        "  - name: acc\n"
        "    metric: accuracy\n"
        "    op: ge\n"
        "    value: 0.5\n"
    )
    cfg = load_thresholds(p)
    assert len(cfg.gates) == 1
    assert cfg.gates[0].metric == "accuracy"
