"""Local llama.cpp reference backend (deferred).

Phase 4 plan keeps this stub so the factory contract is complete. Implementation
lands when a team member needs the local reference path (offline runs, AVeriTeC-2
leaderboard submission, or NFR-Repro-1 bit-identical reproducibility).

See docs/adr/0002-inference-runtime.md for the rationale.
"""
from __future__ import annotations

from typing import TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class LlamaCppBackend:
    def __init__(self, *_args: object, **_kwargs: object) -> None:
        raise NotImplementedError(
            "LlamaCppBackend is not implemented in this phase. "
            "Use MISINFO_BACKEND=groq (primary) or =mock (tests). "
            "See docs/adr/0002-inference-runtime.md."
        )

    @property
    def model_id(self) -> str:  # pragma: no cover
        raise NotImplementedError

    @property
    def model_version(self) -> str | None:  # pragma: no cover
        raise NotImplementedError

    def generate(self, *_args: object, **_kwargs: object) -> str:  # pragma: no cover
        raise NotImplementedError

    def generate_structured(self, *_args: object, **_kwargs: object) -> T:  # pragma: no cover
        raise NotImplementedError
