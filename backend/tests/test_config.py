"""
Tests for configuration management
"""

import pytest
import os
from unittest.mock import patch

from config.settings import Settings, AIServiceType, OCRServiceType, CloudProvider

class TestSettings:
    """Test settings configuration"""
    
    def test_default_settings(self):
        """Test default settings values"""
        settings = Settings()
        
        assert settings.ai_service_type == AIServiceType.LOCAL
        assert settings.ocr_service_type == OCRServiceType.TESSERACT
        assert settings.cloud_provider == CloudProvider.CHUTES_AI
        assert settings.max_file_size == 10 * 1024 * 1024
        assert settings.async_processing is True
    
    @patch.dict(os.environ, {
        'AI_SERVICE_TYPE': 'cloud',
        'OCR_SERVICE_TYPE': 'mistral',
        'CLOUD_PROVIDER': 'bittensor',
        'CHUTES_AI_API_KEY': 'test_key',
        'MISTRAL_API_KEY': 'mistral_key'
    })
    def test_cloud_configuration(self):
        """Test cloud service configuration"""
        settings = Settings.from_env()
        
        assert settings.ai_service_type == AIServiceType.CLOUD
        assert settings.ocr_service_type == OCRServiceType.MISTRAL
        assert settings.cloud_provider == CloudProvider.BITTENSOR
        assert settings.chutes_ai_api_key == 'test_key'
        assert settings.mistral_api_key == 'mistral_key'
    
    def test_ai_model_config_local(self):
        """Test AI model configuration for local mode"""
        settings = Settings(ai_service_type=AIServiceType.LOCAL)
        config = settings.get_ai_model_config()
        
        assert config['provider'] == 'local'
        assert 'extraction_model' in config
        assert 'insights_model' in config
    
    def test_ai_model_config_cloud(self):
        """Test AI model configuration for cloud mode"""
        settings = Settings(
            ai_service_type=AIServiceType.CLOUD,
            cloud_provider=CloudProvider.CHUTES_AI,
            chutes_ai_api_key='test_key'
        )
        config = settings.get_ai_model_config()
        
        assert config['provider'] == 'chutes_ai'
        assert config['api_key'] == 'test_key'
    
    def test_ocr_config_tesseract(self):
        """Test OCR configuration for Tesseract"""
        settings = Settings(ocr_service_type=OCRServiceType.TESSERACT)
        config = settings.get_ocr_config()
        
        assert config['provider'] == 'tesseract'
        assert 'cmd' in config
    
    def test_ocr_config_mistral(self):
        """Test OCR configuration for Mistral"""
        settings = Settings(
            ocr_service_type=OCRServiceType.MISTRAL,
            mistral_api_key='test_key'
        )
        config = settings.get_ocr_config()
        
        assert config['provider'] == 'mistral'
        assert config['api_key'] == 'test_key'
    
    def test_mode_checks(self):
        """Test mode checking methods"""
        local_settings = Settings(ai_service_type=AIServiceType.LOCAL)
        cloud_settings = Settings(ai_service_type=AIServiceType.CLOUD)
        
        assert local_settings.is_local_mode() is True
        assert local_settings.is_cloud_mode() is False
        
        assert cloud_settings.is_local_mode() is False
        assert cloud_settings.is_cloud_mode() is True