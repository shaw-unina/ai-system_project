"""Phase 11 — prompt-injection mitigations on the LLM path.

Two pieces:

* :func:`sanitize_claim` collapses the user-supplied claim into a single line,
  strips zero-width / control characters, and caps length so a malicious
  multi-line payload can't escape the delimited block we wrap it in.
* :func:`wrap_user_content` puts the sanitized claim inside an explicit
  ``<<<USER_CLAIM>>> … <<<END_USER_CLAIM>>>`` fence the prompt template
  references, making instruction-following on user content harder.

The aggregator/decomposer call ``wrap_user_content`` before interpolation.
"""
from __future__ import annotations

import re
import unicodedata

_CONTROL_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]")
_ZW_RE = re.compile(r"[​-‏‪-‮⁦-⁩﻿]")
_FENCE_RE = re.compile(r"<<<\s*(?:end_)?user_claim\s*>>>", re.IGNORECASE)
_MAX_INLINE_LEN = 4000


def sanitize_claim(claim: str) -> str:
    if not isinstance(claim, str):
        raise TypeError("claim must be str")
    s = unicodedata.normalize("NFKC", claim)
    s = _ZW_RE.sub("", s)
    s = _CONTROL_RE.sub(" ", s)
    s = _FENCE_RE.sub("[fence-stripped]", s)
    s = re.sub(r"\s+", " ", s).strip()
    if len(s) > _MAX_INLINE_LEN:
        s = s[:_MAX_INLINE_LEN]
    return s


def wrap_user_content(claim: str) -> str:
    """Returns the sanitized claim wrapped in a labelled fence. Templates that
    interpolate ``{claim}`` get the fence verbatim — the surrounding system
    text instructs the model to treat the fenced region as data, not
    instructions."""
    return f"<<<USER_CLAIM>>>\n{sanitize_claim(claim)}\n<<<END_USER_CLAIM>>>"


__all__ = ("sanitize_claim", "wrap_user_content")
