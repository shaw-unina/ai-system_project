import pytest

pytest.importorskip("fastapi")

from fastapi.testclient import TestClient

from tests.conftest_api import make_test_app


def test_claim_too_long_rejected():
    app = make_test_app()
    client = TestClient(app)
    r = client.post("/v1/verify", json={"claim": "x" * 4001})
    assert r.status_code == 422


def test_missing_claim_rejected():
    app = make_test_app()
    client = TestClient(app)
    r = client.post("/v1/verify", json={})
    assert r.status_code == 422


def test_extra_field_rejected():
    app = make_test_app()
    client = TestClient(app)
    r = client.post("/v1/verify", json={"claim": "ok", "extra": 1})
    assert r.status_code == 422
