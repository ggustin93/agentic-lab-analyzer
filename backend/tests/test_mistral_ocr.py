"""
Tests for Mistral OCR service
"""

import pytest
from unittest.mock import Mock, patch, AsyncMock
import base64
from io import BytesIO
from PIL import Image

from services.mistral_ocr_service import MistralOCRService

class TestMistralOCRService:
    """Test Mistral OCR service"""
    
    @pytest.fixture
    def mock_mistral_client(self):
        """Mock Mistral client"""
        with patch('services.mistral_ocr_service.Mistral') as mock_mistral:
            mock_client = Mock()
            mock_mistral.return_value = mock_client
            yield mock_client
    
    @pytest.fixture
    def ocr_service(self, mock_mistral_client):
        """Create OCR service with mocked client"""
        with patch('services.mistral_ocr_service.MISTRAL_AVAILABLE', True):
            with patch('services.mistral_ocr_service.settings') as mock_settings:
                mock_settings.mistral_api_key = 'test_key'
                mock_settings.mistral_ocr_model = 'mistral-ocr-2505'
                service = MistralOCRService()
                service.client = mock_mistral_client
                return service
    
    def test_is_available_with_client(self, ocr_service):
        """Test availability check with valid client"""
        assert ocr_service.is_available() is True
    
    def test_is_available_without_client(self):
        """Test availability check without client"""
        with patch('services.mistral_ocr_service.MISTRAL_AVAILABLE', False):
            service = MistralOCRService()
            assert service.is_available() is False
    
    @pytest.mark.asyncio
    async def test_extract_text_from_image_success(self, ocr_service, tmp_path):
        """Test successful image text extraction"""
        # Create test image
        img = Image.new('RGB', (100, 100), color='white')
        img_path = tmp_path / "test.png"
        img.save(img_path)
        
        # Mock OCR response
        mock_page = Mock()
        mock_page.markdown = "Test extracted text"
        mock_response = Mock()
        mock_response.pages = [mock_page]
        
        ocr_service.client.ocr.process.return_value = mock_response
        
        result = await ocr_service.extract_text_from_image(str(img_path))
        
        assert result == "Test extracted text"
        ocr_service.client.ocr.process.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_extract_text_from_pdf_success(self, ocr_service, tmp_path):
        """Test successful PDF text extraction"""
        # Create test PDF file
        pdf_path = tmp_path / "test.pdf"
        pdf_path.write_bytes(b"fake pdf content")
        
        # Mock file upload and OCR response
        mock_upload = Mock()
        mock_upload.id = "file_123"
        ocr_service.client.files.upload.return_value = mock_upload
        
        mock_signed_url = Mock()
        mock_signed_url.url = "https://example.com/signed_url"
        ocr_service.client.files.get_signed_url.return_value = mock_signed_url
        
        mock_page = Mock()
        mock_page.markdown = "PDF extracted text"
        mock_response = Mock()
        mock_response.pages = [mock_page]
        ocr_service.client.ocr.process.return_value = mock_response
        
        result = await ocr_service.extract_text_from_pdf(str(pdf_path))
        
        assert "PDF extracted text" in result
        ocr_service.client.files.upload.assert_called_once()
        ocr_service.client.ocr.process.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_extract_text_unsupported_format(self, ocr_service):
        """Test extraction with unsupported file format"""
        with pytest.raises(Exception, match="Unsupported file type"):
            await ocr_service.extract_text("/path/to/file.txt", "txt")
    
    @pytest.mark.asyncio
    async def test_extract_text_service_unavailable(self, tmp_path):
        """Test extraction when service is unavailable"""
        service = MistralOCRService()
        service.client = None
        
        img_path = tmp_path / "test.png"
        img = Image.new('RGB', (100, 100), color='white')
        img.save(img_path)
        
        with pytest.raises(Exception, match="Mistral OCR service not available"):
            await service.extract_text_from_image(str(img_path))
    
    def test_get_usage_info(self, ocr_service):
        """Test usage information retrieval"""
        info = ocr_service.get_usage_info()
        
        assert info['provider'] == 'mistral'
        assert info['model'] == 'mistral-ocr-2505'
        assert info['available'] is True
        assert '.pdf' in info['supported_formats']
        assert '.png' in info['supported_formats']