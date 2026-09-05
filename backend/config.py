import os
from typing import List
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Application Basics
    APP_NAME: str = "VAANIRAKSHAK AI Threat Engine"
    APP_VERSION: str = "1.0.0-SIH2026"
    DEBUG: bool = True
    API_V1_PREFIX: str = "/api/v1"
    ALLOWED_ORIGINS: List[str] = ["*"]

    # Redis Configuration
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    REDIS_SESSION_TTL_SEC: int = 1800  # 30 minutes

    # Database Configuration (PostgreSQL / Supabase or SQLite fallback)
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "sqlite+aiosqlite:///./vaanirakshak.db"
    )

    # Security & Tokens
    SECRET_KEY: str = os.getenv("SECRET_KEY", "vaanirakshak-sih2026-super-secret-key-change-in-prod")
    ALGORITHM: str = "HS256"

    # Configurable Defense Policy Parameters (DECOUPLED FROM ML MODELS)
    INTERVENTION_WINDOW_SEC: int = 10  # 10-second emergency countdown
    RISK_THRESHOLD_CRITICAL: int = 90
    RISK_THRESHOLD_HIGH: int = 80
    RISK_THRESHOLD_MEDIUM: int = 60
    RISK_THRESHOLD_LOW: int = 30

    # Model Parameters
    AUDIO_SAMPLE_RATE: int = 16000
    AUDIO_FRAME_DURATION_SEC: float = 1.0

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore"
    )


settings = Settings()
