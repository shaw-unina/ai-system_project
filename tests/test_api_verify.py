import pytest

pytest.importorskip("fastapi")

from fastapi.testclient import TestClient

from tests.conftest_api import make_test_app


def test_verify_happy_path():
    app = make_test_app(verdict="Supported", confidence=0.85)
    client = TestClient(app)
    r = client.post("/v1/verify", json={"claim": "Paris is the capital of France."})
    assert r.status_code == 200
    body = r.json()
    assert body["verdict"] == "Supported"
    assert body["disclosure"] == "ai_generated"
    assert body["low_confidence"] is False
    assert body["request_id"]
    assert r.headers["X-Request-Id"] == body["request_id"]
    assert body["latency_ms"] >= 0


def test_low_confidence_flag_set():
    app = make_test_app(verdict="Supported", confidence=0.3)
    client = TestClient(app)
    r = client.post("/v1/verify", json={"claim": "weak claim"})
    assert r.status_code == 200
    assert r.json()["low_confidence"] is True


def test_request_id_propagation():
    app = make_test_app()
    client = TestClient(app)
    r = client.post(
        "/v1/verify",
        json={"claim": "ok"},
        headers={"X-Request-Id": "fixed-id-123"},
    )
    assert r.json()["request_id"] == "fixed-id-123"
    assert r.headers["X-Request-Id"] == "fixed-id-123"
