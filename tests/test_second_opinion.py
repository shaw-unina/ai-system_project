"""Phase 11.1 — /v1/second-opinion endpoint."""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from misinfo.config import get_settings
from misinfo.integrations.google_factcheck import (
    FactCheckEntry,
    FactCheckUnavailable,
)
from misinfo.services import second_opinion as so
from misinfo.services.api import create_app
from misinfo.services.auth import reset_rate_limiter
from misinfo.services.deps import get_factchecker

from tests.conftest_api import build_mock_factchecker


@pytest.fixture
def client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.delenv("MISINFO_API_KEYS", raising=False)
    get_settings.cache_clear()
    reset_rate_limiter()
    so.reset_cache()
    app = create_app()
    app.dependency_overrides[get_factchecker] = build_mock_factchecker
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()
        get_settings.cache_clear()
        so.reset_cache()


def test_disabled_when_no_key_set(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GOOGLE_FACT_CHECK_API_KEY", "")
    get_settings.cache_clear()
    r = client.get("/v1/second-opinion", params={"claim": "vaccines cause autism"})
    assert r.status_code == 200
    body = r.json()
    assert body["source"] == "disabled"
    assert body["results"] == []


def test_returns_results_from_client(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GOOGLE_FACT_CHECK_API_KEY", "test-key")
    get_settings.cache_clear()

    def fake_search(self, query, *, max_results=5, language_code="en"):
        return [
            FactCheckEntry(
                publisher="PolitiFact",
                rating="False",
                review_url="https://politifact.com/x",
                review_date="2024-08-12",
                claim_text="claim",
                language="en",
            )
        ]

    monkeypatch.setattr(
        "misinfo.integrations.google_factcheck.GoogleFactCheckClient.search",
        fake_search,
    )

    r = client.get("/v1/second-opinion", params={"claim": "anything"})
    assert r.status_code == 200
    body = r.json()
    assert body["source"] == "google_fact_check_tools_v1alpha1"
    assert len(body["results"]) == 1
    assert body["results"][0]["publisher"] == "PolitiFact"


def test_unavailable_on_upstream_failure(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GOOGLE_FACT_CHECK_API_KEY", "test-key")
    get_settings.cache_clear()

    def boom(self, query, *, max_results=5, language_code="en"):
        raise FactCheckUnavailable("boom")

    monkeypatch.setattr(
        "misinfo.integrations.google_factcheck.GoogleFactCheckClient.search", boom
    )
    r = client.get("/v1/second-opinion", params={"claim": "x"})
    assert r.status_code == 200
    assert r.json()["source"] == "unavailable"


def test_results_are_cached(client: TestClient, monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("GOOGLE_FACT_CHECK_API_KEY", "test-key")
    get_settings.cache_clear()
    calls = {"n": 0}

    def fake_search(self, query, *, max_results=5, language_code="en"):
        calls["n"] += 1
        return []

    monkeypatch.setattr(
        "misinfo.integrations.google_factcheck.GoogleFactCheckClient.search", fake_search
    )

    client.get("/v1/second-opinion", params={"claim": "same claim"})
    client.get("/v1/second-opinion", params={"claim": "same claim"})
    assert calls["n"] == 1
