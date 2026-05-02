from pydantic import BaseModel

from misinfo.inference.cache import CachingBackend


class _Out(BaseModel):
    value: int = 0


class _Counter:
    def __init__(self) -> None:
        self.calls = 0

    @property
    def model_id(self) -> str:
        return "counter-test"

    @property
    def model_version(self) -> str | None:
        return "v1"

    def generate(self, prompt, *, max_tokens=512, temperature=0.0, seed=None):  # noqa: ARG002
        self.calls += 1
        return f"resp-{self.calls}"

    def generate_structured(self, prompt, schema, *, max_tokens=512, temperature=0.0, seed=None):  # noqa: ARG002
        self.calls += 1
        return schema(value=self.calls)


def test_cache_hits_avoid_recomputation(tmp_path, monkeypatch):
    from misinfo import config

    monkeypatch.setenv("DATA_DIR", str(tmp_path))
    config.get_settings.cache_clear()

    inner = _Counter()
    cache = CachingBackend(inner)
    a = cache.generate("hello", seed=1)
    b = cache.generate("hello", seed=1)
    assert a == b
    assert inner.calls == 1

    s1 = cache.generate_structured("p", _Out, seed=2)
    s2 = cache.generate_structured("p", _Out, seed=2)
    assert s1.value == s2.value
    # +1 for the structured call; second hits the cache
    assert inner.calls == 2

    config.get_settings.cache_clear()
