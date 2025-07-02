"""
Configuration management for Health Document Analyzer
Supports cloud (Chutes.ai) and local (Ollama) AI services with easy switching
"""

from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    """Application settings for the IBA MVP (Cloud-First Deployment)."""
    MISTRAL_API_KEY: str
    CHUTES_AI_API_KEY: str
    SUPABASE_URL: str
    SUPABASE_KEY: str
    SUPABASE_BUCKET_NAME: str = "health-docs"
    CHUTES_AI_ENDPOINT: str = "https://llm.chutes.ai/v1"
    CHUTES_AI_MODEL: str = "chutesai/Mistral-Small-3.2-24B-Instruct-2506"
    MISTRAL_OCR_MODEL: str = "mistral-ocr-latest"
    UPLOAD_DIR: str = "uploads"
    model_config = SettingsConfigDict(env_file=".env", extra='ignore')

settings = Settings()