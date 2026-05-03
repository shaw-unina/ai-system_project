"""FactChecker dependency. Cached so all requests share one instance."""
from __future__ import annotations

from functools import lru_cache
from typing import Any, Callable


_FACTORY: Callable[[], Any] | None = None
_INSTANCE: Any | None = None


def set_factchecker_factory(factory: Callable[[], Any]) -> None:
    """Override the FactChecker factory (used by tests)."""
    global _FACTORY, _INSTANCE
    _FACTORY = factory
    _INSTANCE = None
    get_factchecker.cache_clear()


def _default_factory() -> Any:
    """Build the default FactChecker from Settings via the CLI builder."""
    from pathlib import Path

    from misinfo.cli import _build_factchecker
    from misinfo.config import REPO_ROOT, get_settings

    s = get_settings()
    corpus_path: Path | None = s.misinfo_corpus_path
    if corpus_path is None and s.misinfo_corpus_profile is not None:
        corpus_path = REPO_ROOT / f"data/processed/{s.misinfo_corpus_profile}_corpus.jsonl"
    return _build_factchecker(corpus_path=corpus_path)


@lru_cache(maxsize=1)
def get_factchecker() -> Any:
    factory = _FACTORY or _default_factory
    return factory()
