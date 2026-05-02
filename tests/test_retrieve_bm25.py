from misinfo.retrieve.bm25 import BM25Retriever
from misinfo.retrieve.corpus import EvidenceCorpus


def _corpus():
    return EvidenceCorpus.from_iterable([
        {"source_id": "a", "text": "the moon is made of cheese"},
        {"source_id": "b", "text": "the sun is a star at the centre of our solar system"},
        {"source_id": "c", "text": "paris is the capital of france"},
    ])


def test_bm25_retrieves_topical_doc():
    r = BM25Retriever(_corpus())
    out = r.retrieve("capital of france", top_k=2)
    assert out and out[0].source_id == "c"


def test_bm25_empty_query():
    r = BM25Retriever(_corpus())
    assert r.retrieve("", top_k=3) == []


def test_bm25_no_match():
    r = BM25Retriever(_corpus())
    out = r.retrieve("xyzzy quux", top_k=3)
    assert out == []
