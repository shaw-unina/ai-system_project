"""BM25 retriever over an EvidenceCorpus.

Implements BM25Okapi inline (no rank_bm25 dep) so tests don't need an extra
install. The implementation matches rank_bm25's defaults (k1=1.5, b=0.75).
"""
from __future__ import annotations

import math
import re
from collections import Counter
from collections.abc import Sequence

from misinfo.retrieve.corpus import EvidenceCorpus
from misinfo.schemas import EvidenceRef

_TOKEN_RE = re.compile(r"\w+")


def _tokenize(text: str) -> list[str]:
    return _TOKEN_RE.findall(text.lower())


class BM25Retriever:
    def __init__(self, corpus: EvidenceCorpus, *, k1: float = 1.5, b: float = 0.75) -> None:
        self._corpus = corpus
        self._k1 = k1
        self._b = b
        self._tokenized: list[list[str]] = [_tokenize(d.text) for d in corpus.documents]
        self._doc_lens = [len(t) for t in self._tokenized]
        self._avgdl = sum(self._doc_lens) / max(1, len(self._doc_lens))
        # Document frequency
        df: Counter[str] = Counter()
        for tokens in self._tokenized:
            df.update(set(tokens))
        n = len(self._tokenized)
        # IDF: BM25 variant from rank_bm25
        self._idf = {
            term: math.log((n - dfi + 0.5) / (dfi + 0.5) + 1.0) for term, dfi in df.items()
        }
        # Per-doc term frequency
        self._tf = [Counter(tokens) for tokens in self._tokenized]

    def _score(self, query_terms: Sequence[str]) -> list[float]:
        scores = [0.0] * len(self._tokenized)
        for i, tf in enumerate(self._tf):
            dl = self._doc_lens[i] or 1
            for term in query_terms:
                if term not in tf:
                    continue
                idf = self._idf.get(term, 0.0)
                f = tf[term]
                num = f * (self._k1 + 1.0)
                den = f + self._k1 * (1.0 - self._b + self._b * dl / self._avgdl)
                scores[i] += idf * num / den
        return scores

    def retrieve(self, query: str, *, top_k: int = 5) -> list[EvidenceRef]:
        terms = _tokenize(query)
        if not terms or not self._corpus.documents:
            return []
        scores = self._score(terms)
        order = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)
        out: list[EvidenceRef] = []
        for idx in order[:top_k]:
            if scores[idx] <= 0:
                break
            doc = self._corpus.documents[idx]
            out.append(
                EvidenceRef(
                    source_id=doc.source_id,
                    url=doc.url,
                    span=doc.text[:1000],
                    score=float(scores[idx]),
                )
            )
        return out
