"""
Configuration management for Health Document Analyzer
Supports cloud (Chutes.ai) and local (Ollama) AI services with easy switching
"""

import os
from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field
from dotenv import load_dotenv

load_dotenv()

class AIServiceType(str, Enum):
    """AI service provider types"""
    CLOUD = "cloud"
    LOCAL = "local"

class OCRServiceType(str, Enum):
    """OCR service provider types"""
    TESSERACT = "tesseract"
    MISTRAL = "mistral"

class CloudProvider(str, Enum):
    """Cloud AI providers"""
    CHUTES_AI = "chutes_ai"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"

class LocalProvider(str, Enum):
    """Local AI providers"""
    OLLAMA = "ollama"
    OPENAI = "openai"  # Can be used locally too

class Settings(BaseModel):
    """Application settings with cloud/local configuration support"""
    
    # Service Configuration
    ai_service_type: AIServiceType = Field(
        default=AIServiceType.LOCAL,
        description="AI service type: cloud or local"
    )
    ocr_service_type: OCRServiceType = Field(
        default=OCRServiceType.TESSERACT,
        description="OCR service type: tesseract or mistral"
    )
    
    # Cloud AI Configuration
    cloud_provider: CloudProvider = Field(
        default=CloudProvider.CHUTES_AI,
        description="Cloud AI provider"
    )
    chutes_ai_api_key: Optional[str] = Field(
        default=None,
        description="Chutes.ai API key"
    )
    chutes_ai_endpoint: str = Field(
        default="https://api.chutes.ai/v1",
        description="Chutes.ai API endpoint"
    )
    
    # Local AI Configuration
    local_provider: LocalProvider = Field(
        default=LocalProvider.OLLAMA,
        description="Local AI provider"
    )
    ollama_base_url: str = Field(
        default="http://localhost:11434",
        description="Ollama server base URL"
    )
    ollama_model: str = Field(
        default="llama3.2",
        description="Ollama model for health analysis"
    )
    ollama_insights_model: str = Field(
        default="qwen2.5-coder:7b",
        description="Ollama model for insights generation"
    )
    
    # OpenAI Configuration (can be used for both local and cloud)
    openai_api_key: Optional[str] = Field(
        default=None,
        description="OpenAI API key"
    )
    openai_model: str = Field(
        default="gpt-4o-mini",
        description="OpenAI model for health analysis"
    )
    openai_base_url: Optional[str] = Field(
        default=None,
        description="Custom OpenAI base URL (for local deployments)"
    )
    
    # Anthropic Configuration
    anthropic_api_key: Optional[str] = Field(
        default=None,
        description="Anthropic API key"
    )
    
    # OCR Configuration
    mistral_api_key: Optional[str] = Field(
        default=None,
        description="Mistral API key for OCR"
    )
    mistral_ocr_model: str = Field(
        default="mistral-ocr-2505",
        description="Mistral OCR model"
    )
    tesseract_cmd: str = Field(
        default="/usr/bin/tesseract",
        description="Tesseract command path"
    )
    
    # File Upload Configuration
    max_file_size: int = Field(
        default=10 * 1024 * 1024,  # 10MB
        description="Maximum file size in bytes"
    )
    upload_dir: str = Field(
        default="uploads",
        description="Upload directory"
    )
    allowed_extensions: set = Field(
        default={'.pdf', '.png', '.jpg', '.jpeg'},
        description="Allowed file extensions"
    )
    
    # Database Configuration
    database_url: str = Field(
        default="sqlite:///./health_analyzer.db",
        description="Database URL"
    )
    
    # Security Configuration
    secret_key: str = Field(
        default="your-secret-key-change-in-production",
        description="Application secret key"
    )
    
    # Monitoring Configuration
    logfire_token: Optional[str] = Field(
        default=None,
        description="Logfire monitoring token"
    )
    enable_monitoring: bool = Field(
        default=True,
        description="Enable application monitoring"
    )
    
    # Performance Configuration
    max_tokens: int = Field(
        default=2000,
        description="Maximum tokens for AI responses"
    )
    async_processing: bool = Field(
        default=True,
        description="Enable async document processing"
    )
    cache_ttl: int = Field(
        default=3600,
        description="Cache TTL in seconds"
    )
    
    class Config:
        env_file = ".env"
        case_sensitive = False

    @classmethod
    def from_env(cls) -> "Settings":
        """Create settings from environment variables"""
        return cls(
            # Service Configuration
            ai_service_type=os.getenv("AI_SERVICE_TYPE", "local"),
            ocr_service_type=os.getenv("OCR_SERVICE_TYPE", "tesseract"),
            
            # Cloud Configuration
            cloud_provider=os.getenv("CLOUD_PROVIDER", "chutes_ai"),
            chutes_ai_api_key=os.getenv("CHUTES_AI_API_KEY"),
            chutes_ai_endpoint=os.getenv("CHUTES_AI_ENDPOINT", "https://api.chutes.ai/v1"),
            
            # Local Configuration
            local_provider=os.getenv("LOCAL_PROVIDER", "ollama"),
            ollama_base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            ollama_model=os.getenv("OLLAMA_MODEL", "llama3.2"),
            ollama_insights_model=os.getenv("OLLAMA_INSIGHTS_MODEL", "qwen2.5-coder:7b"),
            
            # OpenAI Configuration
            openai_api_key=os.getenv("OPENAI_API_KEY"),
            openai_model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            openai_base_url=os.getenv("OPENAI_BASE_URL"),
            anthropic_api_key=os.getenv("ANTHROPIC_API_KEY"),
            
            # OCR Configuration
            mistral_api_key=os.getenv("MISTRAL_API_KEY"),
            mistral_ocr_model=os.getenv("MISTRAL_OCR_MODEL", "mistral-ocr-2505"),
            tesseract_cmd=os.getenv("TESSERACT_CMD", "/usr/bin/tesseract"),
            
            # File Configuration
            max_file_size=int(os.getenv("MAX_FILE_SIZE", "10485760")),
            upload_dir=os.getenv("UPLOAD_DIR", "uploads"),
            
            # Database Configuration
            database_url=os.getenv("DATABASE_URL", "sqlite:///./health_analyzer.db"),
            
            # Security Configuration
            secret_key=os.getenv("SECRET_KEY", "your-secret-key-change-in-production"),
            
            # Monitoring Configuration
            logfire_token=os.getenv("LOGFIRE_TOKEN"),
            enable_monitoring=os.getenv("ENABLE_MONITORING", "true").lower() == "true",
            
            # Performance Configuration
            max_tokens=int(os.getenv("MAX_TOKENS", "2000")),
            async_processing=os.getenv("ASYNC_PROCESSING", "true").lower() == "true",
            cache_ttl=int(os.getenv("CACHE_TTL", "3600")),
        )

    def get_ai_model_config(self) -> Dict[str, Any]:
        """Get AI model configuration based on service type"""
        if self.ai_service_type == AIServiceType.CLOUD:
            if self.cloud_provider == CloudProvider.CHUTES_AI:
                return {
                    "provider": "chutes_ai",
                    "api_key": self.chutes_ai_api_key,
                    "endpoint": self.chutes_ai_endpoint,
                    "model": "chutes-health-analyzer"
                }
            elif self.cloud_provider == CloudProvider.OPENAI:
                return {
                    "provider": "openai",
                    "api_key": self.openai_api_key,
                    "model": self.openai_model,
                    "base_url": None  # Use default OpenAI endpoint
                }
            elif self.cloud_provider == CloudProvider.ANTHROPIC:
                return {
                    "provider": "anthropic",
                    "api_key": self.anthropic_api_key,
                    "model": "claude-3-haiku-20240307"
                }
        
        # Local configuration
        if self.local_provider == LocalProvider.OLLAMA:
            return {
                "provider": "ollama",
                "base_url": self.ollama_base_url,
                "extraction_model": self.ollama_model,
                "insights_model": self.ollama_insights_model
            }
        elif self.local_provider == LocalProvider.OPENAI:
            return {
                "provider": "openai",
                "api_key": self.openai_api_key,
                "model": self.openai_model,
                "base_url": self.openai_base_url  # Could be local endpoint
            }

    def get_ocr_config(self) -> Dict[str, Any]:
        """Get OCR configuration based on service type"""
        if self.ocr_service_type == OCRServiceType.MISTRAL:
            return {
                "provider": "mistral",
                "api_key": self.mistral_api_key,
                "model": self.mistral_ocr_model
            }
        
        # Tesseract configuration
        return {
            "provider": "tesseract",
            "cmd": self.tesseract_cmd
        }

    def is_cloud_mode(self) -> bool:
        """Check if running in cloud mode"""
        return self.ai_service_type == AIServiceType.CLOUD

    def is_local_mode(self) -> bool:
        """Check if running in local mode"""
        return self.ai_service_type == AIServiceType.LOCAL

    def get_pydantic_ai_model(self) -> str:
        """Get PydanticAI model string based on configuration"""
        if self.is_local_mode() and self.local_provider == LocalProvider.OLLAMA:
            # Return Ollama model configuration for PydanticAI
            return f"openai:{self.ollama_model}"
        elif self.openai_api_key:
            return f"openai:{self.openai_model}"
        else:
            # Fallback to a basic model
            return "openai:gpt-3.5-turbo"

# Global settings instance
settings = Settings.from_env()