from misinfo.eval import metrics as M


def test_accuracy_and_f1_perfect():
    y = ["Supported", "Refuted", "NotEnoughEvidence"]
    assert M.accuracy(y, y) == 1.0
    assert M.f1_macro(y, y) == 1.0


def test_accuracy_zero():
    assert M.accuracy(["a", "b"], ["b", "a"]) == 0.0


def test_ece_well_calibrated_is_small():
    confs = [0.05, 0.95]
    correct = [False, True]
    assert M.ece(confs, correct) < 0.1


def test_mce_bounded():
    confs = [0.99, 0.99, 0.99, 0.99]
    correct = [False, False, False, False]  # confident but always wrong
    assert M.mce(confs, correct) > 0.9


def test_aurc_monotonic():
    # All correct → risk 0 everywhere → AURC = 0
    assert M.aurc([0.9, 0.8, 0.7], [True, True, True]) == 0.0


def test_accuracy_at_coverage():
    confs = [0.9, 0.8, 0.1, 0.2]
    correct = [True, True, False, False]
    assert M.accuracy_at_coverage(confs, correct, 0.5) == 1.0


def test_averitec_recall_proxy():
    y_true = ["Supported", "Refuted", "NotEnoughEvidence"]
    y_pred = ["Supported", "Supported", "NotEnoughEvidence"]
    # Only "Supported" recall counts (1/1 supported correct, 0/1 refuted correct → 1/2)
    assert M.averitec_recall_proxy(y_true, y_pred) == 0.5
