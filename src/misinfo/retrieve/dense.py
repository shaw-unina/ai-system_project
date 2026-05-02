"""Dense retriever using sentence-transformers BGE-small.

Lazy-imports `sentence_transformers` so tests / the base install don't pay
the ~500 MB cost of torch + sentence-transformers.
"""
from __future__ import annotations

from typing import Any

import numpy as np

from misinfo.retrieve.corpus import EvidenceCorpus
from misinfo.schemas import EvidenceRef

DEFAULT_MODEL = "BAAI/bge-small-en-v1.5"


class DenseRetriever:
    def __init__(
        self,
        corpus: EvidenceCorpus,
        *,
        model_name: str = DEFAULT_MODEL,
        encoder: Any | None = None,
    ) -> None:
        self._corpus = corpus
        self._encoder = encoder or self._load_encoder(model_name)
        if corpus.documents:
            self._matrix = self._encode(corpus.texts(), is_query=False)
        else:
            self._matrix = np.zeros((0, 0), dtype=np.float32)

    @staticmethod
    def _load_encoder(model_name: str) -> Any:
        from sentence_transformers import SentenceTransformer  # type: ignore[import-not-found]

        return SentenceTransformer(model_name)

    def _encode(self, texts: list[str], *, is_query: bool) -> np.ndarray:
        # bge-* models recommend a query prefix; harmless on others.
        if is_query:
            texts = [f"Represent this sentence for searching relevant passages: {t}" for t in texts]
        emb = self._encoder.encode(texts, normalize_embeddings=True)
        return np.asarray(emb, dtype=np.float32)

    def retrieve(self, query: str, *, top_k: int = 5) -> list[EvidenceRef]:
        if self._matrix.size == 0:
            return []
        q = self._encode([query], is_query=True)[0]
        sims = self._matrix @ q
        order = np.argsort(-sims)[:top_k]
        out: list[EvidenceRef] = []
        for idx in order:
            doc = self._corpus.documents[int(idx)]
            out.append(
                EvidenceRef(
                    source_id=doc.source_id,
                    url=doc.url,
                    span=doc.text[:1000],
                    score=float(sims[idx]),
                )
            )
        return out
