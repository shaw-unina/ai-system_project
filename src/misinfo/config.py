from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

REPO_ROOT = Path(__file__).resolve().parents[2]

Backend = Literal["groq", "llama_cpp", "mock"]


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

    # Phase 4 (revised) — inference backend + observability
    misinfo_backend: Backend = "groq"
    misinfo_cache: bool = True
    groq_api_key: str | None = Field(default=None)
    groq_model: str = "llama-3.3-70b-versatile"
    groq_fallback_model: str = "qwen/qwen-2.5-32b"

    langfuse_host: str | None = Field(default=None)
    langfuse_public_key: str | None = Field(default=None)
    langfuse_secret_key: str | None = Field(default=None)

    # Azure OpenAI — credentials only; no backend implementation in this phase.
    azure_openai_api_key: str | None = Field(default=None)
    azure_openai_endpoint: str | None = Field(default=None)
    azure_openai_api_version: str | None = Field(default=None)
    azure_openai_deployment: str | None = Field(default=None)


@lru_cache
def get_settings() -> Settings:
    return Settings()
