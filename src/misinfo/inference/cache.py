"""File-based response cache for any LanguageModel.

Cache key: sha256(model_id || prompt || max_tokens || temperature || seed || schema_hash).
Default location: <data_dir>/cache/<backend>/<key>.json — gitignored.
"""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import TypeVar

from pydantic import BaseModel

from misinfo.config import get_settings
from misinfo.inference.base import LanguageModel

T = TypeVar("T", bound=BaseModel)


def _cache_dir(backend_id: str) -> Path:
    s = get_settings()
    p = s.data_dir / "cache" / backend_id
    p.mkdir(parents=True, exist_ok=True)
    return p


def _hash_inputs(*parts: object) -> str:
    h = hashlib.sha256()
    for p in parts:
        h.update(repr(p).encode("utf-8"))
        h.update(b"||")
    return h.hexdigest()


class CachingBackend:
    """Wraps any LanguageModel; reads from / writes to disk."""

    def __init__(self, inner: LanguageModel) -> None:
        self._inner = inner
        self._dir = _cache_dir(inner.model_id.replace("/", "_"))

    @property
    def model_id(self) -> str:
        return self._inner.model_id

    @property
    def model_version(self) -> str | None:
        return self._inner.model_version

    def _key_path(self, key: str) -> Path:
        return self._dir / f"{key}.json"

    def generate(
        self,
        prompt: str,
        *,
        max_tokens: int = 512,
        temperature: float = 0.0,
        seed: int | None = None,
    ) -> str:
        key = _hash_inputs(self.model_id, "generate", prompt, max_tokens, temperature, seed)
        path = self._key_path(key)
        if path.exists():
            return json.loads(path.read_text())["response"]
        out = self._inner.generate(
            prompt, max_tokens=max_tokens, temperature=temperature, seed=seed
        )
        path.write_text(json.dumps({"response": out, "model_version": self.model_version}))
        return out

    def generate_structured(
        self,
        prompt: str,
        schema: type[T],
        *,
        max_tokens: int = 512,
        temperature: float = 0.0,
        seed: int | None = None,
    ) -> T:
        schema_hash = hashlib.sha256(
            json.dumps(schema.model_json_schema(), sort_keys=True).encode()
        ).hexdigest()[:16]
        key = _hash_inputs(
            self.model_id, "structured", schema.__name__, schema_hash,
            prompt, max_tokens, temperature, seed,
        )
        path = self._key_path(key)
        if path.exists():
            data = json.loads(path.read_text())
            return schema.model_validate_json(data["response"])
        obj = self._inner.generate_structured(
            prompt, schema, max_tokens=max_tokens, temperature=temperature, seed=seed
        )
        path.write_text(json.dumps({
            "response": obj.model_dump_json(),
            "model_version": self.model_version,
        }))
        return obj


def maybe_wrap(inner: LanguageModel) -> LanguageModel:
    """Return a CachingBackend if the cache is enabled in Settings, else `inner`."""
    if get_settings().misinfo_cache:
        return CachingBackend(inner)
    return inner
