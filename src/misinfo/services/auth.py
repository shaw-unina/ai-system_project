"""Phase 11 — bearer-token auth + per-key sliding-window rate limiting.

Auth is opt-in: if `MISINFO_API_KEYS` is empty/unset, both `require_api_key`
and `enforce_rate_limit` no-op so existing local dev and the test suite keep
working unchanged.
"""
from __future__ import annotations

import time
from collections import deque
from threading import Lock
from typing import Iterable

from fastapi import Header, HTTPException, Request, status

from misinfo.config import get_settings


def _allowed_keys() -> set[str]:
    raw = get_settings().misinfo_api_keys or ""
    return {k.strip() for k in raw.split(",") if k.strip()}


def _extract_bearer(authorization: str | None) -> str | None:
    if not authorization:
        return None
    parts = authorization.split(None, 1)
    if len(parts) != 2 or parts[0].lower() != "bearer":
        return None
    return parts[1].strip() or None


def require_api_key(authorization: str | None = Header(default=None)) -> str:
    """FastAPI dependency. Returns the verified key (or the literal ``"anonymous"``
    when auth is disabled) so downstream code can use it as a rate-limit bucket."""
    keys = _allowed_keys()
    if not keys:
        return "anonymous"
    token = _extract_bearer(authorization)
    if token is None or token not in keys:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="missing or invalid bearer token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return token


class _SlidingWindow:
    def __init__(self, window_s: float = 60.0) -> None:
        self.window_s = window_s
        self._hits: dict[str, deque[float]] = {}
        self._lock = Lock()

    def hit(self, key: str, limit: int, now: float | None = None) -> tuple[bool, int, float]:
        """Returns ``(allowed, remaining, retry_after_s)``."""
        if limit <= 0:
            return True, 1_000_000, 0.0
        t = time.monotonic() if now is None else now
        cutoff = t - self.window_s
        with self._lock:
            dq = self._hits.setdefault(key, deque())
            while dq and dq[0] < cutoff:
                dq.popleft()
            if len(dq) >= limit:
                retry = max(0.0, dq[0] + self.window_s - t)
                return False, 0, retry
            dq.append(t)
            return True, max(0, limit - len(dq)), 0.0

    def reset(self) -> None:
        with self._lock:
            self._hits.clear()


_LIMITER = _SlidingWindow(window_s=60.0)


def reset_rate_limiter() -> None:
    """Test hook."""
    _LIMITER.reset()


def enforce_rate_limit(
    request: Request,
    key: str = "anonymous",
) -> None:
    s = get_settings()
    if not _allowed_keys():
        return
    allowed, remaining, retry = _LIMITER.hit(key, s.misinfo_rate_limit_per_min)
    request.state.rate_limit_remaining = remaining
    request.state.rate_limit_limit = s.misinfo_rate_limit_per_min
    if not allowed:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail="rate limit exceeded",
            headers={"Retry-After": str(int(retry) + 1)},
        )


def metrics_token_check(authorization: str | None) -> None:
    """If a metrics token is configured, gate ``/metrics`` on it; otherwise open
    (Prometheus inside the compose network is the typical local case)."""
    expected = get_settings().misinfo_metrics_token
    if not expected:
        return
    token = _extract_bearer(authorization)
    if token != expected:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="missing or invalid metrics token",
            headers={"WWW-Authenticate": "Bearer"},
        )


__all__: Iterable[str] = (
    "require_api_key",
    "enforce_rate_limit",
    "metrics_token_check",
    "reset_rate_limiter",
)
