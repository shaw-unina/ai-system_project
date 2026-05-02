from misinfo.eval.reliability import reliability_bins, risk_coverage_curve


def test_reliability_bins_empty():
    assert reliability_bins([], []) == []


def test_reliability_bins_well_calibrated():
    # 50 samples per decile, accuracy ≈ midpoint of bin
    confs = []
    correct = []
    for b in range(10):
        mid = (b + 0.5) / 10.0
        n = 50
        confs.extend([mid] * n)
        n_correct = int(round(mid * n))
        correct.extend([True] * n_correct + [False] * (n - n_correct))
    bins = reliability_bins(confs, correct, n_bins=10)
    populated = [b for b in bins if b.n > 0]
    # Each populated bin's accuracy should be close to its mean confidence
    for b in populated:
        assert abs(b.accuracy - b.confidence) < 0.05


def test_risk_coverage_curve_shape():
    confs = [0.9, 0.8, 0.5, 0.3]
    correct = [True, True, False, False]
    curve = risk_coverage_curve(confs, correct)
    assert len(curve) == 4
    assert curve[0][0] < curve[-1][0]  # coverage grows
