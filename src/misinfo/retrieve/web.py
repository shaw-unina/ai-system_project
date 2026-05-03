"""Phase 11.1 — live web retriever.

Conforms to the :class:`Retriever` protocol so it drops into the existing
pipeline. On Tavily failure returns an empty list (caller degrades to
``Abstain`` via the existing low-evidence path) — no 5xx propagation.

A small in-process LRU cache keyed by ``sha256(query)`` collapses repeated
look-ups within a process; the orchestrator already issues per-sub-question
queries so the same claim hits the cache on the second sub-question.
"""
from __future__ import annotations

import hashlib
import logging
from collections import OrderedDict
from threading import Lock

from misinfo.integrations.tavily import TavilyClient, TavilyResult, TavilyUnavailable
from misinfo.schemas import EvidenceRef

logger = logging.getLogger(__name__)


class _TTLCache:
    """Tiny capped LRU. No TTL pruning — capacity is the only bound."""

    def __init__(self, capacity: int = 256) -> None:
        self._cap = capacity
        self._d: "OrderedDict[str, list[TavilyResult]]" = OrderedDict()
        self._lock = Lock()

    def get(self, key: str) -> list[TavilyResult] | None:
        with self._lock:
            v = self._d.get(key)
            if v is not None:
                self._d.move_to_end(key)
            return v

    def put(self, key: str, value: list[TavilyResult]) -> None:
        with self._lock:
            self._d[key] = value
            self._d.move_to_end(key)
            while len(self._d) > self._cap:
                self._d.popitem(last=False)


class WebRetriever:
    def __init__(
        self,
        client: TavilyClient,
        *,
        max_span_chars: int = 1200,
        cache_capacity: int = 256,
    ) -> None:
        self._client = client
        self._max_span = max_span_chars
        self._cache = _TTLCache(capacity=cache_capacity)

    def retrieve(self, query: str, *, top_k: int = 5) -> list[EvidenceRef]:
        if not query.strip():
            return []
        key = hashlib.sha256(query.encode("utf-8")).hexdigest()
        cached = self._cache.get(key)
        if cached is None:
            try:
                cached = self._client.search(query, max_results=max(top_k, 5))
            except TavilyUnavailable as exc:
                logger.warning("web retriever degrade-to-empty: %s", exc)
                cached = []
            self._cache.put(key, cached)
        return [_to_evidence(i, r, self._max_span) for i, r in enumerate(cached[:top_k])]


def _to_evidence(idx: int, r: TavilyResult, max_span: int) -> EvidenceRef:
    span = (r.content or r.title)[:max_span]
    source_id = f"web-{idx}-{hashlib.sha256(r.url.encode()).hexdigest()[:8]}"
    return EvidenceRef(source_id=source_id, url=r.url or None, span=span, score=r.score)


__all__ = ("WebRetriever",)
