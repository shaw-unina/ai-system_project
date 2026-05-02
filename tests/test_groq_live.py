"""Live Groq smoke test. Skipped unless `--run-live` and GROQ_API_KEY are set."""
from __future__ import annotations

import os

import pytest

pytestmark = pytest.mark.live


def test_groq_generate_smoke():
    if not os.environ.get("GROQ_API_KEY"):
        pytest.skip("GROQ_API_KEY not set")
    from misinfo.inference.groq_backend import GroqBackend

    b = GroqBackend()
    out = b.generate("Reply with the single word: ok", max_tokens=8, temperature=0.0)
    assert isinstance(out, str) and len(out) > 0
