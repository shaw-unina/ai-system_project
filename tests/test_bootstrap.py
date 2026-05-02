from misinfo.eval import metrics as M
from misinfo.eval.bootstrap import (
    bootstrap_ci,
    holm_correct,
    paired_bootstrap_diff,
)


def test_paired_bootstrap_identical_predictions_brackets_zero():
    y = ["a", "b", "a", "b", "a", "b", "a", "b"] * 4
    res = paired_bootstrap_diff(M.accuracy, y, y, y, n=200, seed=0)
    assert res.point == 0.0
    assert res.ci_low <= 0.0 <= res.ci_high


def test_paired_bootstrap_p_value_orders_with_effect():
    y_true = ["a"] * 50 + ["b"] * 50
    y_better = list(y_true)  # perfect
    y_worse = ["a"] * 50 + ["a"] * 50  # always 'a'
    better = paired_bootstrap_diff(M.accuracy, y_true, y_better, y_worse, n=200, seed=0)
    worse = paired_bootstrap_diff(M.accuracy, y_true, y_worse, y_better, n=200, seed=0)
    assert better.point > worse.point
    assert better.p_value < worse.p_value


def test_paired_bootstrap_seed_determinism():
    y = ["a", "b"] * 30
    a = paired_bootstrap_diff(M.accuracy, y, y, list(reversed(y)), n=300, seed=7)
    b = paired_bootstrap_diff(M.accuracy, y, y, list(reversed(y)), n=300, seed=7)
    assert a == b


def test_bootstrap_ci_brackets_point():
    y = ["a"] * 100
    point, lo, hi = bootstrap_ci(M.accuracy, y, y, n=200, seed=0)
    assert lo <= point <= hi


def test_holm_correct_monotonic():
    p = [0.01, 0.04, 0.03, 0.5]
    adj = holm_correct(p)
    assert all(0.0 <= x <= 1.0 for x in adj)
    # Holm adjusted p-values are non-decreasing in the *sorted* order; check a specific inequality
    assert adj[3] >= adj[0]
