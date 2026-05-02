import pytest

from misinfo.inference import LanguageModel, MockBackend, get_backend


def test_mock_backend_resolves() -> None:
    b = get_backend("mock")
    assert isinstance(b, MockBackend)
    assert isinstance(b, LanguageModel)
    assert b.model_id == "mock"
    assert b.model_version == "0"


def test_mock_generate_is_deterministic() -> None:
    b = MockBackend()
    out1 = b.generate("hello", seed=1)
    out2 = b.generate("hello", seed=1)
    out3 = b.generate("hello", seed=2)
    assert out1 == out2
    assert out1 != out3


def test_unknown_backend_raises() -> None:
    with pytest.raises(ValueError):
        get_backend("nope")  # type: ignore[arg-type]


def test_groq_backend_lazy_imports(monkeypatch) -> None:
    """Importing the package should not require the `groq` extra to be installed."""
    monkeypatch.setenv("MISINFO_BACKEND", "mock")
    # If groq_backend module imported groq at top-level, this would fail in a clean env.
    import importlib

    mod = importlib.import_module("misinfo.inference.groq_backend")
    assert hasattr(mod, "GroqBackend")


def test_llama_cpp_backend_is_stub() -> None:
    from misinfo.inference.llama_cpp_backend import LlamaCppBackend
    with pytest.raises(NotImplementedError):
        LlamaCppBackend()
