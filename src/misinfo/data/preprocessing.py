from __future__ import annotations

import unicodedata

PREPROCESSING_VERSION = "1"
DEFAULT_MAX_CHARS = 4000


def normalize_text(text: str) -> str:
    """NFC unicode normalize + collapse internal whitespace."""
    if text is None:
        return ""
    text = unicodedata.normalize("NFC", text)
    text = " ".join(text.split())
    return text.strip()


def clip_text(text: str, max_chars: int = DEFAULT_MAX_CHARS) -> str:
    """Hard character clip per SCOPE.md (≤4000 chars)."""
    if max_chars < 0:
        raise ValueError("max_chars must be non-negative")
    return text[:max_chars]


def preprocess_claim(text: str, max_chars: int = DEFAULT_MAX_CHARS) -> str:
    """Idempotent claim preprocessing: normalize then clip."""
    return clip_text(normalize_text(text), max_chars)
