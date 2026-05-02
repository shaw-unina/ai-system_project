import pytest

pytest.importorskip("fastapi")

from fastapi.testclient import TestClient

from tests.conftest_api import make_test_app


def test_metrics_includes_request_counter():
    app = make_test_app()
    client = TestClient(app)
    client.post("/v1/verify", json={"claim": "hello"})
    r = client.get("/metrics")
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("text/plain")
    body = r.text
    assert "misinfo_requests_total" in body
    assert "misinfo_latency_seconds_bucket" in body
    assert "misinfo_verdicts_total" in body


def test_metrics_increments_per_request():
    app = make_test_app()
    client = TestClient(app)
    for _ in range(3):
        client.post("/v1/verify", json={"claim": "x"})
    body = client.get("/metrics").text
    # Find the verify counter line
    line = next(
        (l for l in body.splitlines()
         if "misinfo_requests_total" in l and 'endpoint="/v1/verify"' in l),
        None,
    )
    assert line is not None
    n = int(line.rsplit(" ", 1)[-1])
    assert n >= 3
