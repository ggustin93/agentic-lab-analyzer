"""
Configuration management for the Health Document Analyzer backend.

STORAGE_MODE selects the persistence adapter (ADR-008): "local" (default,
SQLite + local folder — no cloud account needed) or "supabase". The Supabase
variables are only required in supabase mode.
"""

from typing import List, Literal, Optional

from pydantic import model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    MISTRAL_API_KEY: str
    CHUTES_AI_API_KEY: str

    STORAGE_MODE: Literal["local", "supabase"] = "local"

    # Local mode (ADR-008)
    DB_PATH: str = "data/app.db"
    UPLOAD_DIR: str = "uploads"
    PUBLIC_BASE_URL: str = "http://localhost:8000"

    # Supabase mode
    SUPABASE_URL: Optional[str] = None
    SUPABASE_KEY: Optional[str] = None
    SUPABASE_BUCKET_NAME: str = "health-docs"

    CORS_ORIGINS: List[str] = ["http://localhost:4200"]

    # Upload limits — enforced server-side (client-side checks are a UX
    # convenience, not a control)
    MAX_FILE_SIZE: int = 10 * 1024 * 1024  # bytes

    CHUTES_AI_ENDPOINT: str = "https://llm.chutes.ai/v1"
    CHUTES_AI_MODEL: str = "chutesai/Mistral-Small-3.2-24B-Instruct-2506"
    MISTRAL_OCR_MODEL: str = "mistral-ocr-latest"

    model_config = SettingsConfigDict(env_file=".env", extra='ignore')

    @model_validator(mode="after")
    def _require_supabase_credentials(self) -> "Settings":
        if self.STORAGE_MODE == "supabase" and not (self.SUPABASE_URL and self.SUPABASE_KEY):
            raise ValueError("STORAGE_MODE=supabase requires SUPABASE_URL and SUPABASE_KEY")
        return self


settings = Settings()
