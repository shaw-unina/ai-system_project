import json

from misinfo import cli


def _write_records(path, n=80, seed=0):
    import numpy as np

    rng = np.random.default_rng(seed)
    with path.open("w", encoding="utf-8") as f:
        for _ in range(n):
            c = float(rng.uniform(0.5, 0.95))
            cov = float(rng.uniform())
            top1 = float(rng.uniform())
            correct = bool(rng.random() < c)
            f.write(json.dumps({
                "verifier_confidence": c,
                "mean_top1": top1,
                "evidence_coverage": cov,
                "correct": correct,
            }) + "\n")


def test_calibrate_temperature_roundtrip(tmp_path):
    rec = tmp_path / "rec.jsonl"
    out = tmp_path / "t.json"
    _write_records(rec)
    rc = cli.main(["calibrate", "--head", "temperature", "--records", str(rec), "--output", str(out)])
    assert rc == 0
    assert out.exists()
    data = json.loads(out.read_text())
    assert "temperature" in data


def test_calibrate_fusion_roundtrip(tmp_path):
    rec = tmp_path / "rec.jsonl"
    out = tmp_path / "fusion.joblib"
    _write_records(rec, n=200)
    rc = cli.main(["calibrate", "--head", "fusion", "--records", str(rec), "--output", str(out)])
    assert rc == 0
    assert out.exists()

    from misinfo.abstention.fusion import LogisticFusionHead
    loaded = LogisticFusionHead.load(out)
    from misinfo.schemas import AggregatorOutput
    agg = AggregatorOutput(verdict="Supported", confidence=0.7, rationale="x")
    _, p = loaded.score(agg, {"mean_top1": 0.5, "evidence_coverage": 0.5})
    assert 0.0 <= p <= 1.0
