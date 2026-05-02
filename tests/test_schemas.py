import pytest
from pydantic import ValidationError

from misinfo.schemas import EvidenceRef, Verdict, VerdictMetadata


def _meta(**overrides) -> VerdictMetadata:
    base = {"backend": "mock", "model_id": "mock"}
    base.update(overrides)
    return VerdictMetadata(**base)


def test_verdict_roundtrip_json() -> None:
    v = Verdict(
        verdict="Supported",
        confidence=0.8,
        evidence=[EvidenceRef(source_id="s1", url=None, span="evidence text", score=0.9)],
        rationale="because evidence supports it",
        metadata=_meta(),
    )
    raw = v.model_dump_json()
    back = Verdict.model_validate_json(raw)
    assert back == v


def test_verdict_rejects_unknown_label() -> None:
    with pytest.raises(ValidationError):
        Verdict(
            verdict="Maybe",  # type: ignore[arg-type]
            confidence=0.5,
            rationale="r",
            metadata=_meta(),
        )


def test_verdict_confidence_in_range() -> None:
    with pytest.raises(ValidationError):
        Verdict(
            verdict="Supported",
            confidence=1.5,
            rationale="r",
            metadata=_meta(),
        )


def test_verdict_forbids_extra() -> None:
    with pytest.raises(ValidationError):
        Verdict.model_validate(
            {
                "verdict": "Supported",
                "confidence": 0.5,
                "rationale": "r",
                "metadata": {"backend": "mock", "model_id": "mock"},
                "wat": True,
            }
        )


def test_metadata_records_backend_and_trace_id() -> None:
    m = _meta(model_version="2026-05-01", langfuse_trace_id="abc123", seed=7, temperature=0.0)
    assert m.backend == "mock"
    assert m.langfuse_trace_id == "abc123"
    assert m.generated_at_utc  # auto-set
