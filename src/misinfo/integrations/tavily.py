"""Phase 11.1 — minimal Tavily client.

Wraps Tavily's ``/search`` endpoint. We only use the bits we need: query,
max_results, and the per-result ``content`` field (Tavily extracts the
relevant text span from each page so we don't have to do a follow-up fetch).

Failures (network, 4xx, 5xx, timeout) raise :class:`TavilyUnavailable`.
Callers map that to "no evidence" rather than 500ing the request — graceful
degrade matters more than upstream error fidelity here.
"""
from __future__ import annotations

import json
import logging
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Iterable

logger = logging.getLogger(__name__)


class TavilyUnavailable(RuntimeError):
    """Raised when Tavily is unreachable / returns a non-2xx response."""


@dataclass(frozen=True)
class TavilyResult:
    title: str
    url: str
    content: str
    score: float


class TavilyClient:
    BASE = "https://api.tavily.com/search"

    def __init__(self, api_key: str, *, timeout_s: float = 8.0) -> None:
        if not api_key:
            raise ValueError("TavilyClient requires a non-empty api_key")
        self._api_key = api_key
        self._timeout_s = timeout_s

    def search(
        self,
        query: str,
        *,
        max_results: int = 5,
        search_depth: str = "basic",
    ) -> list[TavilyResult]:
        payload = {
            "api_key": self._api_key,
            "query": query,
            "max_results": max_results,
            "search_depth": search_depth,
            "include_answer": False,
            "include_raw_content": False,
        }
        body = json.dumps(payload).encode("utf-8")
        req = urllib.request.Request(
            self.BASE,
            data=body,
            method="POST",
            headers={"content-type": "application/json"},
        )
        try:
            with urllib.request.urlopen(req, timeout=self._timeout_s) as r:
                raw = r.read()
        except (urllib.error.URLError, TimeoutError) as exc:
            raise TavilyUnavailable(f"tavily unreachable: {exc}") from exc
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise TavilyUnavailable("tavily returned non-json") from exc
        return [_to_result(r) for r in data.get("results", [])]


def _to_result(r: dict) -> TavilyResult:
    return TavilyResult(
        title=str(r.get("title") or ""),
        url=str(r.get("url") or ""),
        content=str(r.get("content") or ""),
        score=float(r.get("score") or 0.0),
    )


__all__: Iterable[str] = ("TavilyClient", "TavilyResult", "TavilyUnavailable")
