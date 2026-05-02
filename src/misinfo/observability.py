"""Project-local Langfuse wrapper.

Goal: a single `@traced(...)` decorator we can sprinkle across pipeline stages and
backend calls. When `LANGFUSE_HOST` is unset (CI, unit tests, offline dev) it is
a no-op so the rest of the codebase remains testable without the Langfuse stack.
"""
from __future__ import annotations

import os
from collections.abc import Callable
from functools import wraps
from typing import Any, ParamSpec, TypeVar

from misinfo.config import get_settings

P = ParamSpec("P")
R = TypeVar("R")


def _langfuse_enabled() -> bool:
    s = get_settings()
    return bool(s.langfuse_host and s.langfuse_public_key and s.langfuse_secret_key)


def _propagate_to_env() -> None:
    """The Langfuse SDK reads keys from os.environ. pydantic-settings loads from
    .env into the Settings object but does not export to os.environ. Bridge that
    once so the SDK sees the same credentials."""
    s = get_settings()
    for env_key, value in (
        ("LANGFUSE_HOST", s.langfuse_host),
        ("LANGFUSE_PUBLIC_KEY", s.langfuse_public_key),
        ("LANGFUSE_SECRET_KEY", s.langfuse_secret_key),
    ):
        if value and not os.environ.get(env_key):
            os.environ[env_key] = value


def _try_import_observe() -> Callable[..., Any] | None:
    if not _langfuse_enabled():
        return None
    _propagate_to_env()
    try:
        from langfuse.decorators import observe  # type: ignore[import-not-found]
        return observe
    except ImportError:
        return None


def traced(name: str | None = None, **observe_kwargs: Any) -> Callable[[Callable[P, R]], Callable[P, R]]:
    """Trace a callable in Langfuse if available, else no-op.

    Usage:
        @traced("decompose")
        def decompose(claim): ...
    """
    observe = _try_import_observe()
    if observe is None:
        def passthrough(fn: Callable[P, R]) -> Callable[P, R]:
            @wraps(fn)
            def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
                return fn(*args, **kwargs)
            return wrapper
        return passthrough

    def decorator(fn: Callable[P, R]) -> Callable[P, R]:
        return observe(name=name or fn.__name__, **observe_kwargs)(fn)
    return decorator


def current_trace_id() -> str | None:
    """Best-effort: return the current Langfuse trace id, or None if disabled."""
    if not _langfuse_enabled():
        return None
    _propagate_to_env()
    try:
        from langfuse.decorators import langfuse_context  # type: ignore[import-not-found]
        return langfuse_context.get_current_trace_id()
    except Exception:
        return None


def flush() -> None:
    """Flush any pending Langfuse events. Call at the end of short-lived processes."""
    if not _langfuse_enabled():
        return
    _propagate_to_env()
    try:
        from langfuse.decorators import langfuse_context  # type: ignore[import-not-found]
        langfuse_context.flush()
    except Exception:
        pass
