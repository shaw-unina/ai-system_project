"""Phase 11.1 — Google Fact Check Tools v1alpha1 client.

We only call ``claims:search``. Callers map ``FactCheckUnavailable`` to an
empty result list so the dashboard can render a "no second opinion" state
gracefully on error.
"""
from __future__ import annotations

import json
import logging
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass

logger = logging.getLogger(__name__)


class FactCheckUnavailable(RuntimeError): ...


@dataclass(frozen=True)
class FactCheckEntry:
    publisher: str
    rating: str
    review_url: str
    review_date: str | None
    claim_text: str
    language: str


class GoogleFactCheckClient:
    BASE = "https://factchecktools.googleapis.com/v1alpha1/claims:search"

    def __init__(self, api_key: str, *, timeout_s: float = 5.0) -> None:
        if not api_key:
            raise ValueError("GoogleFactCheckClient requires a non-empty api_key")
        self._api_key = api_key
        self._timeout_s = timeout_s

    def search(
        self,
        query: str,
        *,
        max_results: int = 5,
        language_code: str = "en",
    ) -> list[FactCheckEntry]:
        params = urllib.parse.urlencode(
            {
                "key": self._api_key,
                "query": query,
                "languageCode": language_code,
                "pageSize": max_results,
            }
        )
        url = f"{self.BASE}?{params}"
        try:
            with urllib.request.urlopen(url, timeout=self._timeout_s) as r:
                raw = r.read()
        except (urllib.error.URLError, TimeoutError) as exc:
            raise FactCheckUnavailable(f"google fc unreachable: {exc}") from exc
        try:
            data = json.loads(raw)
        except json.JSONDecodeError as exc:
            raise FactCheckUnavailable("google fc returned non-json") from exc
        return _normalize(data, max_results=max_results)


def _normalize(data: dict, *, max_results: int) -> list[FactCheckEntry]:
    out: list[FactCheckEntry] = []
    for claim in (data.get("claims") or [])[:max_results]:
        claim_text = str(claim.get("text") or "")
        for rev in claim.get("claimReview") or []:
            publisher = (rev.get("publisher") or {}).get("name") or "(unknown)"
            out.append(
                FactCheckEntry(
                    publisher=str(publisher),
                    rating=str(rev.get("textualRating") or ""),
                    review_url=str(rev.get("url") or ""),
                    review_date=(rev.get("reviewDate") or None),
                    claim_text=claim_text,
                    language=str(rev.get("languageCode") or "en"),
                )
            )
            if len(out) >= max_results:
                return out
    return out


__all__ = ("GoogleFactCheckClient", "FactCheckEntry", "FactCheckUnavailable")
