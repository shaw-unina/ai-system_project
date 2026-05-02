import pytest

from misinfo.data.registry import REGISTRY, DatasetSpec, get_spec, register


def test_known_specs_present() -> None:
    assert "averitec@v2" in REGISTRY
    assert "fakenewsnet@politifact-text" in REGISTRY
    assert "attack-set@v0" in REGISTRY


def test_get_spec_returns_known() -> None:
    spec = get_spec("averitec", "v2")
    assert spec.license == "CC-BY-SA-4.0"
    assert "dev" in spec.splits


def test_get_spec_unknown_raises() -> None:
    with pytest.raises(KeyError):
        get_spec("nonexistent", "v0")


def test_register_duplicate_raises() -> None:
    spec = DatasetSpec(name="averitec", version="v2", license="x", homepage="x")
    with pytest.raises(ValueError):
        register(spec)


def test_key_format() -> None:
    spec = DatasetSpec(name="foo", version="bar", license="x", homepage="x")
    assert spec.key == "foo@bar"
