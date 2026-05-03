"""Phase 11.1 — WebRetriever degrades gracefully on Tavily failure."""
from __future__ import annotations

from misinfo.integrations.tavily import TavilyResult, TavilyUnavailable
from misinfo.retrieve.web import WebRetriever


class _FakeClient:
    def __init__(self, results=None, raises=None) -> None:
        self._results = results or []
        self._raises = raises
        self.calls = 0

    def search(self, query: str, *, max_results: int = 5):
        self.calls += 1
        if self._raises is not None:
            raise self._raises
        return self._results


def test_retrieve_returns_evidence_refs() -> None:
    client = _FakeClient(
        results=[
            TavilyResult(
                title="Eiffel Tower",
                url="https://en.wikipedia.org/wiki/Eiffel_Tower",
                content="The Eiffel Tower is in Paris.",
                score=0.9,
            ),
            TavilyResult(
                title="Paris",
                url="https://en.wikipedia.org/wiki/Paris",
                content="Paris is the capital of France.",
                score=0.7,
            ),
        ]
    )
    r = WebRetriever(client)  # type: ignore[arg-type]
    refs = r.retrieve("where is the eiffel tower", top_k=2)
    assert len(refs) == 2
    assert refs[0].url == "https://en.wikipedia.org/wiki/Eiffel_Tower"
    assert "Eiffel Tower is in Paris" in refs[0].span
    assert refs[0].score == 0.9


def test_retrieve_caches_repeat_query() -> None:
    client = _FakeClient(results=[])
    r = WebRetriever(client)  # type: ignore[arg-type]
    r.retrieve("repeat me")
    r.retrieve("repeat me")
    assert client.calls == 1


def test_retrieve_degrades_on_unavailable() -> None:
    client = _FakeClient(raises=TavilyUnavailable("boom"))
    r = WebRetriever(client)  # type: ignore[arg-type]
    assert r.retrieve("anything") == []


def test_retrieve_empty_query_short_circuits() -> None:
    client = _FakeClient(results=[])
    r = WebRetriever(client)  # type: ignore[arg-type]
    assert r.retrieve("   ") == []
    assert client.calls == 0
