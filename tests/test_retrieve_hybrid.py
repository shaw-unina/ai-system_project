from misinfo.retrieve.hybrid import HybridRetriever, reciprocal_rank_fusion
from misinfo.schemas import EvidenceRef


def _ref(sid: str, score: float = 1.0) -> EvidenceRef:
    return EvidenceRef(source_id=sid, span="x", score=score)


def test_rrf_promotes_consensus():
    a = [_ref("a"), _ref("b"), _ref("c")]
    b = [_ref("b"), _ref("a"), _ref("d")]
    fused = reciprocal_rank_fusion([a, b], k=60)
    sids = [ref.source_id for ref, _ in fused]
    # 'a' and 'b' both appear in top of both; should outrank 'c' and 'd'
    assert set(sids[:2]) == {"a", "b"}


class _StubRetriever:
    def __init__(self, refs):
        self._refs = refs

    def retrieve(self, query, *, top_k=5):  # noqa: ARG002
        return self._refs[:top_k]


def test_hybrid_combines_two_retrievers():
    r1 = _StubRetriever([_ref("a"), _ref("b")])
    r2 = _StubRetriever([_ref("b"), _ref("c")])
    h = HybridRetriever(r1, r2)
    out = h.retrieve("q", top_k=3)
    assert {e.source_id for e in out} == {"a", "b", "c"}
    assert out[0].source_id == "b"  # only consensus item
