"""Phase 11 — bearer-token auth + rate limiting on the FastAPI service."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from misinfo.config import get_settings
from misinfo.services.api import create_app
from misinfo.services.auth import reset_rate_limiter
from misinfo.services.deps import get_factchecker

from tests.conftest_api import build_mock_factchecker


@pytest.fixture
def client_with_keys(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setenv("MISINFO_API_KEYS", "k-alpha,k-beta")
    monkeypatch.setenv("MISINFO_RATE_LIMIT_PER_MIN", "5")
    get_settings.cache_clear()
    reset_rate_limiter()
    app = create_app()
    app.dependency_overrides[get_factchecker] = build_mock_factchecker
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()
        get_settings.cache_clear()
        reset_rate_limiter()


@pytest.fixture
def client_without_keys(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.delenv("MISINFO_API_KEYS", raising=False)
    get_settings.cache_clear()
    reset_rate_limiter()
    app = create_app()
    app.dependency_overrides[get_factchecker] = build_mock_factchecker
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()
        get_settings.cache_clear()


def test_verify_requires_bearer_when_keys_configured(client_with_keys: TestClient) -> None:
    r = client_with_keys.post("/v1/verify", json={"claim": "hello"})
    assert r.status_code == 401


def test_verify_rejects_wrong_token(client_with_keys: TestClient) -> None:
    r = client_with_keys.post(
        "/v1/verify",
        json={"claim": "hello"},
        headers={"Authorization": "Bearer not-a-real-key"},
    )
    assert r.status_code == 401


def test_verify_accepts_valid_token(client_with_keys: TestClient) -> None:
    r = client_with_keys.post(
        "/v1/verify",
        json={"claim": "hello"},
        headers={"Authorization": "Bearer k-alpha"},
    )
    assert r.status_code == 200


def test_verify_open_when_no_keys_configured(client_without_keys: TestClient) -> None:
    r = client_without_keys.post("/v1/verify", json={"claim": "hello"})
    assert r.status_code == 200


def test_healthz_is_unauthenticated(client_with_keys: TestClient) -> None:
    assert client_with_keys.get("/healthz").status_code == 200


def test_rate_limit_returns_429_after_quota(client_with_keys: TestClient) -> None:
    headers = {"Authorization": "Bearer k-alpha"}
    statuses = [
        client_with_keys.post("/v1/verify", json={"claim": "x"}, headers=headers).status_code
        for _ in range(7)
    ]
    assert statuses.count(200) == 5
    assert statuses.count(429) == 2


def test_rate_limit_is_per_key(client_with_keys: TestClient) -> None:
    a = {"Authorization": "Bearer k-alpha"}
    b = {"Authorization": "Bearer k-beta"}
    for _ in range(5):
        assert client_with_keys.post("/v1/verify", json={"claim": "x"}, headers=a).status_code == 200
    assert client_with_keys.post("/v1/verify", json={"claim": "x"}, headers=b).status_code == 200


def test_metrics_token_gate(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("MISINFO_API_KEYS", "k1")
    monkeypatch.setenv("MISINFO_METRICS_TOKEN", "scrape-me")
    get_settings.cache_clear()
    reset_rate_limiter()
    app = create_app()
    app.dependency_overrides[get_factchecker] = build_mock_factchecker
    client = TestClient(app)
    try:
        assert client.get("/metrics").status_code == 401
        ok = client.get("/metrics", headers={"Authorization": "Bearer scrape-me"})
        assert ok.status_code == 200
    finally:
        app.dependency_overrides.clear()
        get_settings.cache_clear()
