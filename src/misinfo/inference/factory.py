from __future__ import annotations

from misinfo.config import Backend, get_settings
from misinfo.inference.base import LanguageModel
from misinfo.inference.cache import maybe_wrap


def _build(backend: Backend) -> LanguageModel:
    if backend == "mock":
        from misinfo.inference.mock_backend import MockBackend
        return MockBackend()

    if backend == "groq":
        from misinfo.inference.groq_backend import GroqBackend
        return GroqBackend()

    if backend == "llama_cpp":
        from misinfo.inference.llama_cpp_backend import LlamaCppBackend
        return LlamaCppBackend()

    raise ValueError(f"Unknown backend: {backend!r}")


def get_backend(backend: Backend | None = None, *, cache: bool | None = None) -> LanguageModel:
    """Resolve and construct a LanguageModel.

    If `backend` is None, reads `Settings.misinfo_backend`. Cache wrapping is
    controlled by `Settings.misinfo_cache`; pass `cache=False` to opt out.
    """
    if backend is None:
        backend = get_settings().misinfo_backend
    inner = _build(backend)
    if cache is False:
        return inner
    return maybe_wrap(inner)
