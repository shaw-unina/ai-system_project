"""Hybrid retriever combining sparse + dense via Reciprocal Rank Fusion."""
from __future__ import annotations

from typing import Protocol, runtime_checkable

from misinfo.schemas import EvidenceRef


@runtime_checkable
class _Retriever(Protocol):
    def retrieve(self, query: str, *, top_k: int = 5) -> list[EvidenceRef]: ...


def reciprocal_rank_fusion(
    rankings: list[list[EvidenceRef]],
    *,
    k: int = 60,
) -> list[tuple[EvidenceRef, float]]:
    """RRF over multiple ranked lists. Returns (evidence, fused_score) sorted desc.

    A single source_id may appear in multiple input lists; we keep the highest-rank
    occurrence of each source_id across lists and sum the RRF contributions.
    """
    fused_score: dict[str, float] = {}
    seen_ref: dict[str, EvidenceRef] = {}
    for ranking in rankings:
        for rank, ref in enumerate(ranking):
            sid = ref.source_id
            fused_score[sid] = fused_score.get(sid, 0.0) + 1.0 / (k + rank + 1)
            if sid not in seen_ref or seen_ref[sid].score < ref.score:
                seen_ref[sid] = ref
    items = sorted(fused_score.items(), key=lambda kv: kv[1], reverse=True)
    return [(seen_ref[sid], score) for sid, score in items]


class HybridRetriever:
    def __init__(self, *retrievers: _Retriever, rrf_k: int = 60) -> None:
        if not retrievers:
            raise ValueError("HybridRetriever needs at least one underlying retriever")
        self._retrievers = retrievers
        self._k = rrf_k

    def retrieve(self, query: str, *, top_k: int = 5, fan_out: int = 50) -> list[EvidenceRef]:
        rankings = [r.retrieve(query, top_k=fan_out) for r in self._retrievers]
        fused = reciprocal_rank_fusion(rankings, k=self._k)
        return [
            EvidenceRef(
                source_id=ref.source_id,
                url=ref.url,
                span=ref.span,
                score=fused_score,
            )
            for ref, fused_score in fused[:top_k]
        ]
