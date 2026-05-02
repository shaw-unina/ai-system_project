import pytest

pytest.importorskip("fastapi")

from fastapi.testclient import TestClient

from misinfo.services.probe import probe_latency
from tests.conftest_api import make_test_app


def test_probe_latency_against_in_process_app():
    app = make_test_app()
    client = TestClient(app)
    report = probe_latency(client, n=5)
    assert report.n == 5
    assert report.errors == 0
    assert report.p50_ms <= report.p95_ms
    assert report.mean_ms >= 0.0
