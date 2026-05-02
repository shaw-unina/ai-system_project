"""Inference backends.

Public API: `LanguageModel` Protocol, `get_backend()` factory.
Concrete backends: `GroqBackend`, `MockBackend`, `LlamaCppBackend` (deferred).
"""
from misinfo.inference.base import LanguageModel
from misinfo.inference.factory import get_backend
from misinfo.inference.mock_backend import MockBackend

__all__ = ["LanguageModel", "get_backend", "MockBackend"]
