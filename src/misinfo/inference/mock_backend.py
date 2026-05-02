from __future__ import annotations

import hashlib
import json
from typing import TypeVar

from pydantic import BaseModel

T = TypeVar("T", bound=BaseModel)


class MockBackend:
    """Deterministic offline backend used for tests and dry-runs.

    `generate` returns a hash-based stub. `generate_structured` constructs the
    pydantic model with the schema's defaults; callers may pass custom factories
    via the `_response_factory` attribute for richer test scenarios.
    """

    def __init__(self, response_factory: object | None = None) -> None:
        self._response_factory = response_factory

    @property
    def model_id(self) -> str:
        return "mock"

    @property
    def model_version(self) -> str | None:
        return "0"

    def generate(
        self,
        prompt: str,
        *,
        max_tokens: int = 512,
        temperature: float = 0.0,
        seed: int | None = None,
    ) -> str:
        h = hashlib.sha256(
            f"{prompt}|{max_tokens}|{temperature}|{seed}".encode()
        ).hexdigest()
        return f"mock-response:{h[:16]}"

    def generate_structured(
        self,
        prompt: str,
        schema: type[T],
        *,
        max_tokens: int = 512,
        temperature: float = 0.0,
        seed: int | None = None,
    ) -> T:
        if callable(self._response_factory):
            obj = self._response_factory(prompt, schema)
            if isinstance(obj, schema):
                return obj
            if isinstance(obj, dict):
                return schema(**obj)
            if isinstance(obj, str):
                return schema(**json.loads(obj))
        # Fallback: schema with all defaults — only works when every field has a default.
        return schema()  # type: ignore[call-arg]
