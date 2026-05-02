from __future__ import annotations

from misinfo.config import Backend, get_settings
from misinfo.inference.base import LanguageModel


def get_backend(backend: Backend | None = None) -> LanguageModel:
    """Resolve and construct a LanguageModel implementation.

    If `backend` is None, reads `Settings.misinfo_backend`.
    """
    if backend is None:
        backend = get_settings().misinfo_backend

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
