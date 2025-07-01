"""
Ultra-Simple MVP Configuration
No database, essential cloud services only
"""

import os
from typing import Optional
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseModel):
    """Ultra-simple MVP settings - Essential only"""
    
    # Chutes.ai Configuration
    chutes_api_token: Optional[str] = Field(
        default=None,
        description="Chutes.ai API token"
    )
    chutes_model: str = Field(
        default="deepseek-ai/DeepSeek-V3-0324",
        description="Chutes.ai model"
    )
    chutes_endpoint: str = Field(
        default="https://llm.chutes.ai/v1/chat/completions",
        description="Chutes.ai endpoint"
    )
    
    # Mistral OCR Configuration
    mistral_api_key: Optional[str] = Field(
        default=None,
        description="Mistral API key"
    )
    mistral_ocr_model: str = Field(
        default="mistral-ocr-latest",
        description="Mistral OCR model"
    )
    
    # File Configuration
    max_file_size: int = Field(default=10 * 1024 * 1024, description="10MB max")
    upload_dir: str = Field(default="uploads", description="Upload directory")
    
    # CORS Configuration
    cors_origins: str = Field(
        default="http://localhost:4200,http://localhost:3000",
        description="CORS origins"
    )
    
    # Logging
    log_level: str = Field(default="INFO", description="Log level")
    
    class Config:
        env_file = ".env"

    @classmethod
    def from_env(cls) -> "Settings":
        """Load from environment"""
        return cls(
            chutes_api_token=os.getenv("CHUTES_API_TOKEN"),
            chutes_model=os.getenv("CHUTES_MODEL", "deepseek-ai/DeepSeek-V3-0324"),
            chutes_endpoint=os.getenv("CHUTES_ENDPOINT", "https://llm.chutes.ai/v1/chat/completions"),
            mistral_api_key=os.getenv("MISTRAL_API_KEY"),
            mistral_ocr_model=os.getenv("MISTRAL_OCR_MODEL", "mistral-ocr-latest"),
            max_file_size=int(os.getenv("MAX_FILE_SIZE", "10485760")),
            upload_dir=os.getenv("UPLOAD_DIR", "uploads"),
            cors_origins=os.getenv("CORS_ORIGINS", "http://localhost:4200,http://localhost:3000"),
            log_level=os.getenv("LOG_LEVEL", "INFO"),
        )
    
    def get_cors_origins_list(self) -> list:
        """Get CORS origins as list"""
        return [origin.strip() for origin in self.cors_origins.split(",")]
    
    def is_configured(self) -> bool:
        """Check if essential services are configured"""
        return self.chutes_api_token is not None and self.mistral_api_key is not None

# Global settings
settings = Settings.from_env()