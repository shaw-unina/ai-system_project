from misinfo.data.attacks.paraphrase import (
    STYLES,
    check_quality_gates,
    length_ratio_ok,
    load_prompt,
    near_duplicate_score,
)


def _always(score):
    return lambda _p, _h: score


def test_styles_have_prompts() -> None:
    for s in STYLES:
        text = load_prompt(s)
        assert "{claim}" in text


def test_near_duplicate_high_for_same_text() -> None:
    s = "The sky is blue and the grass is green."
    assert near_duplicate_score(s, s) == 1.0


def test_near_duplicate_low_for_disjoint() -> None:
    assert near_duplicate_score("alpha beta gamma", "delta epsilon zeta") == 0.0


def test_length_band() -> None:
    assert length_ratio_ok("a" * 100, "b" * 80)
    assert not length_ratio_ok("a" * 100, "b" * 30)
    assert not length_ratio_ok("a" * 100, "b" * 250)


def test_quality_gate_passes_good_paraphrase() -> None:
    original = "The mayor announced a new transportation plan in March 2024."
    paraphrase = "In March 2024, the mayor unveiled a transportation initiative."
    res = check_quality_gates(original, paraphrase, nli_predictor=_always(0.9))
    assert res.passed, res.reasons
    assert res.nli_score == 0.9
    assert res.length_ok


def test_quality_gate_rejects_near_duplicate() -> None:
    original = "The mayor announced a new transportation plan."
    near_copy = "The mayor announced a new transportation plan!"
    res = check_quality_gates(original, near_copy, nli_predictor=_always(0.99))
    assert not res.passed
    assert any("near_duplicate" in r for r in res.reasons)


def test_quality_gate_rejects_low_nli() -> None:
    original = "The mayor announced a new transportation plan."
    paraphrase = "Local government budget shortfall worsens this quarter."
    res = check_quality_gates(original, paraphrase, nli_predictor=_always(0.2))
    assert not res.passed
    assert any("nli" in r for r in res.reasons)


def test_quality_gate_rejects_length_violation() -> None:
    original = "The mayor announced a new transportation plan in March."
    too_long = original + " " + " ".join(["extra"] * 200)
    res = check_quality_gates(original, too_long, nli_predictor=_always(0.95))
    assert not res.passed
    assert "length_out_of_band" in res.reasons
