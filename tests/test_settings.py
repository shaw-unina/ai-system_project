from misinfo.config import Settings, get_settings


def test_defaults() -> None:
    s = get_settings()
    assert s.env == "dev"
    assert s.random_seed == 42
    assert s.log_level == "INFO"


def test_env_override(monkeypatch) -> None:
    monkeypatch.setenv("RANDOM_SEED", "123")
    monkeypatch.setenv("LOG_LEVEL", "DEBUG")
    s = Settings()
    assert s.random_seed == 123
    assert s.log_level == "DEBUG"
