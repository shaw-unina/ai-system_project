from __future__ import annotations

from typing import Protocol, TypeVar, runtime_checkable

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


@runtime_checkable
class LanguageModel(Protocol):
    """A pluggable LLM backend. Implementations live under misinfo.inference."""

    @property
    def model_id(self) -> str: ...

    @property
    def model_version(self) -> str | None: ...

    def generate(
        self,
        prompt: str,
        *,
        max_tokens: int = 512,
        temperature: float = 0.0,
        seed: int | None = None,
    ) -> str: ...

    def generate_structured(
        self,
        prompt: str,
        schema: type[T],
        *,
        max_tokens: int = 512,
        temperature: float = 0.0,
        seed: int | None = None,
    ) -> T: ...
