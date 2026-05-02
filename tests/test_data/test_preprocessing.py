from misinfo.data.preprocessing import (
    DEFAULT_MAX_CHARS,
    clip_text,
    normalize_text,
    preprocess_claim,
)


def test_normalize_collapses_whitespace() -> None:
    assert normalize_text("  hello   world\t\n") == "hello world"


def test_normalize_nfc() -> None:
    # decomposed "é" (e + combining acute) normalizes to composed form
    decomposed = "café"
    composed = "café"
    assert normalize_text(decomposed) == composed


def test_normalize_handles_none() -> None:
    assert normalize_text(None) == ""  # type: ignore[arg-type]


def test_clip_respects_limit() -> None:
    assert clip_text("a" * 5000, max_chars=10) == "a" * 10


def test_default_clip_is_4000() -> None:
    assert len(clip_text("x" * 5000)) == DEFAULT_MAX_CHARS


def test_preprocess_is_idempotent() -> None:
    raw = "  Some\nClaim   with  spaces  "
    once = preprocess_claim(raw)
    twice = preprocess_claim(once)
    assert once == twice
