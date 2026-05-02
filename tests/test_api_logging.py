import pytest

pytest.importorskip("fastapi")

from fastapi.testclient import TestClient
from loguru import logger

from tests.conftest_api import make_test_app


def _capture_log_records(monkeypatch):
    records: list[dict] = []
    sink_id = logger.add(lambda msg: records.append(msg.record), level="DEBUG")
    return records, sink_id


def test_claim_redacted_by_default(monkeypatch):
    monkeypatch.setenv("MISINFO_LOG_CLAIMS", "false")
    app = make_test_app()
    client = TestClient(app)
    records, sink_id = _capture_log_records(monkeypatch)
    try:
        client.post("/v1/verify", json={"claim": "SECRET-TOKEN-AAAA"})
        all_text = "\n".join(
            str(r.get("extra", {})) + " " + str(r.get("message", "")) for r in records
        )
        assert "SECRET-TOKEN-AAAA" not in all_text
        assert "redacted" in all_text
    finally:
        logger.remove(sink_id)


def test_claim_logged_when_enabled(monkeypatch):
    monkeypatch.setenv("MISINFO_LOG_CLAIMS", "true")
    app = make_test_app()
    client = TestClient(app)
    records, sink_id = _capture_log_records(monkeypatch)
    try:
        client.post("/v1/verify", json={"claim": "VISIBLE-TOKEN-BBBB"})
        all_text = "\n".join(str(r.get("extra", {})) for r in records)
        assert "VISIBLE-TOKEN-BBBB" in all_text
    finally:
        logger.remove(sink_id)
