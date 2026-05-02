"""Groq inference backend.

Uses the `groq` Python SDK (OpenAI-compatible). Reads credentials and model
choice from `misinfo.config.Settings`. JSON-mode for structured output, with one
retry on parse failure before raising.

This module imports `groq` lazily so the rest of the codebase stays importable
when `groq` is not installed (e.g. in CI without the `inference` extra).
"""
from __future__ import annotations

import json
from typing import Any, TypeVar

from pydantic import BaseModel, ValidationError

from misinfo.config import get_settings
from misinfo.observability import traced

T = TypeVar("T", bound=BaseModel)


class GroqBackend:
    def __init__(self, model: str | None = None, fallback_model: str | None = None) -> None:
        s = get_settings()
        if not s.groq_api_key:
            raise RuntimeError(
                "GROQ_API_KEY is not set. Set it in .env or environment, "
                "or switch backend with MISINFO_BACKEND=mock."
            )
        try:
            from groq import Groq  # type: ignore[import-not-found]
        except ImportError as e:
            raise RuntimeError(
                "`groq` package not installed. Install with `pip install '.[inference]'`."
            ) from e
        self._client = Groq(api_key=s.groq_api_key)
        self._model = model or s.groq_model
        self._fallback = fallback_model or s.groq_fallback_model
        self._last_model_version: str | None = None

    @property
    def model_id(self) -> str:
        return self._model

    @property
    def model_version(self) -> str | None:
        return self._last_model_version

    @traced("groq.generate")
    def generate(
        self,
        prompt: str,
        *,
        max_tokens: int = 512,
        temperature: float = 0.0,
        seed: int | None = None,
    ) -> str:
        response = self._client.chat.completions.create(
            model=self._model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=temperature,
            seed=seed,
        )
        self._last_model_version = getattr(response, "model", None)
        return response.choices[0].message.content or ""

    @traced("groq.generate_structured")
    def generate_structured(
        self,
        prompt: str,
        schema: type[T],
        *,
        max_tokens: int = 512,
        temperature: float = 0.0,
        seed: int | None = None,
    ) -> T:
        instructions = (
            prompt
            + "\n\nRespond with a single JSON object matching this schema:\n"
            + json.dumps(schema.model_json_schema(), indent=2)
        )
        last_err: Exception | None = None
        for attempt in range(2):
            response = self._client.chat.completions.create(
                model=self._model,
                messages=[{"role": "user", "content": instructions}],
                max_tokens=max_tokens,
                temperature=temperature,
                seed=seed,
                response_format={"type": "json_object"},
            )
            self._last_model_version = getattr(response, "model", None)
            raw = response.choices[0].message.content or "{}"
            try:
                return schema.model_validate_json(raw)
            except (ValidationError, json.JSONDecodeError) as e:
                last_err = e
                continue
        raise RuntimeError(f"GroqBackend failed to produce valid {schema.__name__}: {last_err}")

    def usage_info(self) -> dict[str, Any]:
        """Latest call's usage stats (best-effort; populated by Langfuse traces too)."""
        return {"model": self._model, "fallback": self._fallback}
