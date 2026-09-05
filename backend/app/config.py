"""
Central application configuration.

All values are sourced from environment variables (see .env.example at the
repository root). Nothing here should ever contain a real secret — this
module only declares shape and safe local-development defaults.
"""

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8", extra="ignore")

    # --- General ---
    app_name: str = "VaaniRakshak Gateway"
    environment: str = "development"
    debug: bool = True

    # --- API ---
    api_v1_prefix: str = "/v1"

    # --- Redis ---
    redis_url: str = "redis://redis:6379/0"

    # --- Database (Supabase/PostgreSQL) ---
    database_url: str = "postgresql+asyncpg://vaanirakshak:vaanirakshak@postgres:5432/vaanirakshak"

    # --- Auth ---
    jwt_secret: str = "changeme-in-env-never-commit-real-secret"
    jwt_algorithm: str = "HS256"

    # --- Policy (see PRD.md section 5, Rules.md section 14) ---
    critical_confirmation_window_seconds: int = 10


@lru_cache
def get_settings() -> Settings:
    return Settings()
