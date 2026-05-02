import pytest

pytest.importorskip("fastapi")

from fastapi.testclient import TestClient

from tests.conftest_api import make_test_app


def test_healthz():
    app = make_test_app()
    client = TestClient(app)
    r = client.get("/healthz")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_readyz():
    app = make_test_app()
    client = TestClient(app)
    r = client.get("/readyz")
    assert r.status_code == 200
    body = r.json()
    assert body["ready"] is True
    assert "backend" in body
    assert body["head"] == "IdentityAbstentionHead"


def test_version():
    app = make_test_app()
    client = TestClient(app)
    r = client.get("/version")
    assert r.status_code == 200
    body = r.json()
    assert body["name"] == "misinfo"
    assert body["version"]
    assert body["model_id"] == "mock"
