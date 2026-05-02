from misinfo.abstention.threshold import records_from_jsonl, select_threshold_for_coverage


def test_select_threshold_keeps_top_half():
    confs = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    tau = select_threshold_for_coverage(confs, 0.5)
    accepted = sum(1 for c in confs if c >= tau)
    assert accepted == 5


def test_select_threshold_full_coverage():
    confs = [0.1, 0.5, 0.9]
    tau = select_threshold_for_coverage(confs, 1.0)
    assert all(c >= tau for c in confs)


def test_records_from_jsonl(tmp_path):
    p = tmp_path / "rec.jsonl"
    p.write_text(
        '{"verifier_confidence": 0.8, "mean_top1": 0.5, "evidence_coverage": 0.6, "correct": true}\n'
        '{"verifier_confidence": 0.3, "mean_top1": 0.1, "evidence_coverage": 0.0, "correct": false}\n'
    )
    rs = records_from_jsonl(p)
    assert len(rs) == 2
    assert rs[0].verifier_confidence == 0.8
    assert rs[1].correct is False
