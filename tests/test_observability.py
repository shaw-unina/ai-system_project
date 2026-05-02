from misinfo.config import get_settings
from misinfo.observability import current_trace_id, traced


def test_traced_is_noop_when_disabled(monkeypatch) -> None:
    """With LANGFUSE_HOST unset, traced(...) must not require the langfuse package."""
    monkeypatch.delenv("LANGFUSE_HOST", raising=False)
    monkeypatch.delenv("LANGFUSE_PUBLIC_KEY", raising=False)
    monkeypatch.delenv("LANGFUSE_SECRET_KEY", raising=False)
    get_settings.cache_clear()

    @traced("test-stage")
    def add(a: int, b: int) -> int:
        return a + b

    assert add(1, 2) == 3


def test_current_trace_id_returns_none_when_disabled(monkeypatch) -> None:
    monkeypatch.delenv("LANGFUSE_HOST", raising=False)
    get_settings.cache_clear()
    assert current_trace_id() is None


def test_traced_preserves_function_metadata() -> None:
    @traced()
    def myfn(x: int) -> int:
        """docstring"""
        return x * 2

    assert myfn.__name__ == "myfn"
    assert myfn.__doc__ == "docstring"
    assert myfn(3) == 6
