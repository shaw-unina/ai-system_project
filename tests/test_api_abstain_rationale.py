import pytest

pytest.importorskip("fastapi")

from fastapi.testclient import TestClient

from tests.conftest_api import make_test_app


def test_abstain_rationale_lists_reasons():
    # confidence (0.3) < tau (0.7) → forced Abstain
    app = make_test_app(verdict="Supported", confidence=0.3, tau=0.7)
    client = TestClient(app)
    r = client.post("/v1/verify", json={"claim": "uncertain claim"})
    assert r.status_code == 200
    body = r.json()
    assert body["verdict"] == "Abstain"
    assert body["rationale"].startswith("Abstained:")
    assert "confidence below threshold" in body["rationale"]
    assert body["low_confidence"] is True
