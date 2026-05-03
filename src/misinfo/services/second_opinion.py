"""Phase 11.1 — `/v1/second-opinion` endpoint.

Display-only sidecar: returns existing third-party fact-checks for a claim
via Google Fact Check Tools. Never feeds back into the verification
pipeline. Always returns 200 — disabled / unavailable / no-results states
are encoded in the response body so the frontend renders them cleanly.

Note on querying: Google Fact Check Tools is keyword-matched, not semantic.
Long, well-formed claims rarely match. We try the original query first;
on no match we fall back to a shortened version (first sentence, then a
keyword-only stub) so realistic claims like the Eiffel Tower paragraph
still surface published reviews.
"""
from __future__ import annotations

import hashlib
import re
import time
from collections import OrderedDict
from threading import Lock
from typing import Literal

from fastapi import APIRouter, Depends, Query, Request
from pydantic import BaseModel, ConfigDict

from misinfo.config import get_settings
from misinfo.integrations.google_factcheck import (
    FactCheckEntry,
    FactCheckUnavailable,
    GoogleFactCheckClient,
)
from misinfo.services.auth import enforce_rate_limit, require_api_key

router = APIRouter()


class SecondOpinionEntry(BaseModel):
    model_config = ConfigDict(extra="forbid")

    publisher: str
    rating: str
    review_url: str
    review_date: str | None = None
    claim_text: str
    language: str


class SecondOpinionResponse(BaseModel):
    model_config = ConfigDict(extra="forbid")

    claim: str
    results: list[SecondOpinionEntry]
    fetched_at: float
    source: Literal["google_fact_check_tools_v1alpha1", "disabled", "unavailable"]
    matched_query: str | None = None  # which query (possibly shortened) returned hits


_WORD_RE = re.compile(r"[A-Za-z][A-Za-z'-]+")


def _candidate_queries(claim: str) -> list[str]:
    """Yield progressively shorter queries.

    Google FC ``claims:search`` is keyword-matched, so a long well-formed
    sentence often returns nothing. We try the original first, then the
    first sentence, then a keyword stub built from the first 8 informative
    words of that sentence.
    """
    out: list[str] = []
    seen: set[str] = set()

    def add(q: str) -> None:
        q = q.strip()
        if q and q.lower() not in seen:
            out.append(q)
            seen.add(q.lower())

    add(claim)
    first_sentence = re.split(r"(?<=[.!?])\s+", claim.strip(), maxsplit=1)[0]
    if first_sentence and first_sentence != claim:
        add(first_sentence)
    words = _WORD_RE.findall(first_sentence or claim)
    if len(words) > 8:
        add(" ".join(words[:8]))
    return out


_CACHE_TTL_S = 24 * 60 * 60
_CACHE_CAP = 1024
_cache: "OrderedDict[str, tuple[float, tuple[list[SecondOpinionEntry], str | None]]]" = OrderedDict()
_cache_lock = Lock()


def _cache_get(
    key: str,
) -> tuple[list[SecondOpinionEntry], str | None] | None:
    now = time.time()
    with _cache_lock:
        v = _cache.get(key)
        if v is None:
            return None
        ts, payload = v
        if now - ts > _CACHE_TTL_S:
            _cache.pop(key, None)
            return None
        _cache.move_to_end(key)
        return payload


def _cache_put(
    key: str, payload: tuple[list[SecondOpinionEntry], str | None]
) -> None:
    with _cache_lock:
        _cache[key] = (time.time(), payload)
        _cache.move_to_end(key)
        while len(_cache) > _CACHE_CAP:
            _cache.popitem(last=False)


def _to_entry(e: FactCheckEntry) -> SecondOpinionEntry:
    return SecondOpinionEntry(
        publisher=e.publisher,
        rating=e.rating,
        review_url=e.review_url,
        review_date=e.review_date,
        claim_text=e.claim_text,
        language=e.language,
    )


@router.get("/v1/second-opinion", response_model=SecondOpinionResponse)
def second_opinion(
    request: Request,
    claim: str = Query(..., min_length=1, max_length=4000),
    max_results: int = Query(5, ge=1, le=20),
    api_key: str = Depends(require_api_key),
) -> SecondOpinionResponse:
    enforce_rate_limit(request, key=api_key)
    s = get_settings()
    if not s.google_fact_check_api_key:
        return SecondOpinionResponse(
            claim=claim, results=[], fetched_at=time.time(), source="disabled"
        )

    cache_key = hashlib.sha256(f"{claim}|{max_results}".encode("utf-8")).hexdigest()
    cached = _cache_get(cache_key)
    if cached is not None:
        entries, matched = cached
        return SecondOpinionResponse(
            claim=claim,
            results=entries,
            fetched_at=time.time(),
            source="google_fact_check_tools_v1alpha1",
            matched_query=matched,
        )

    client = GoogleFactCheckClient(s.google_fact_check_api_key)
    entries: list[SecondOpinionEntry] = []
    matched: str | None = None
    for q in _candidate_queries(claim):
        try:
            raw = client.search(q, max_results=max_results)
        except FactCheckUnavailable:
            return SecondOpinionResponse(
                claim=claim, results=[], fetched_at=time.time(), source="unavailable"
            )
        if raw:
            entries = [_to_entry(e) for e in raw]
            matched = q
            break

    _cache_put(cache_key, (entries, matched))
    return SecondOpinionResponse(
        claim=claim,
        results=entries,
        fetched_at=time.time(),
        source="google_fact_check_tools_v1alpha1",
        matched_query=matched,
    )


def reset_cache() -> None:
    """Test hook."""
    with _cache_lock:
        _cache.clear()
