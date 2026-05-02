import pytest

pytest.importorskip("fastapi")

from fastapi.testclient import TestClient

from tests.conftest_api import make_test_app


def test_batch_returns_n_results_in_order():
    app = make_test_app()
    client = TestClient(app)
    claims = [f"claim {i}" for i in range(5)]
    r = client.post("/v1/batch", json={"claims": claims})
    assert r.status_code == 200
    body = r.json()
    assert len(body["results"]) == 5
    for res in body["results"]:
        assert res["verdict"] in ("Supported", "Refuted", "NotEnoughEvidence", "Abstain")


def test_batch_too_large_rejected():
    app = make_test_app()
    client = TestClient(app)
    r = client.post("/v1/batch", json={"claims": ["c"] * 101})
    assert r.status_code == 422


def test_batch_empty_rejected():
    app = make_test_app()
    client = TestClient(app)
    r = client.post("/v1/batch", json={"claims": []})
    assert r.status_code == 422
