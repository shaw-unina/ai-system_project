from functools import lru_cache
from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

REPO_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    env: str = "dev"
    data_dir: Path = REPO_ROOT / "data"
    models_dir: Path = REPO_ROOT / "models"
    random_seed: int = 42
    log_level: str = "INFO"

    openai_api_key: str | None = Field(default=None)
    hf_token: str | None = Field(default=None)


@lru_cache
def get_settings() -> Settings:
    return Settings()
