"""
Tests for Mistral OCR service
"""

import pytest
from unittest.mock import patch, MagicMock
from PIL import Image
import os
import base64

from services.mistral_ocr_service import MistralOCRService

@pytest.fixture
def mock_requests_post():
    """Mock requests.post"""
    with patch('services.mistral_ocr_service.requests.post') as mock_post:
        yield mock_post

@pytest.fixture
def mistral_service():
    """Fixture for MistralOCRService"""
    return MistralOCRService()

class TestMistralOCRService:
    """Test suite for the MistralOCRService."""

    def test_is_available_with_key(self, mistral_service):
        """Test that the service is available when an API key is provided."""
        assert mistral_service.is_available() is True

    def test_is_available_without_key(self):
        """Test that the service is unavailable when the API key is missing."""
        with patch('services.mistral_ocr_service.settings.MISTRAL_API_KEY', new=''):
            service = MistralOCRService()
            assert service.is_available() is False

    @pytest.mark.asyncio
    async def test_extract_text_from_image_success(self, mistral_service, mock_requests_post, tmp_path):
        """Test successful text extraction from an image."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "pages": [{"index": 0, "markdown": "Extracted text from image."}]
        }
        mock_requests_post.return_value = mock_response

        img_path = tmp_path / "test.png"
        Image.new('RGB', (100, 100)).save(img_path)
        
        result = mistral_service.extract_text(str(img_path), 'png')
        assert "Extracted text from image." in result
        mock_requests_post.assert_called_once()

    @pytest.mark.asyncio
    async def test_extract_text_from_pdf_success(self, mistral_service, mock_requests_post, tmp_path):
        """Test successful text extraction from a PDF."""
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "pages": [{"index": 0, "markdown": "Extracted text from PDF."}]
        }
        mock_requests_post.return_value = mock_response

        pdf_path = tmp_path / "test.pdf"
        with open(pdf_path, "wb") as f:
            f.write(b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n") # Minimal PDF

        result = mistral_service.extract_text(str(pdf_path), 'pdf')
        assert "Extracted text from PDF." in result
        mock_requests_post.assert_called_once()
        
    def test_extract_text_service_unavailable(self):
        """Test extraction when service is unavailable."""
        with patch('services.mistral_ocr_service.settings.MISTRAL_API_KEY', new=''):
            service = MistralOCRService()
            with pytest.raises(Exception, match="Mistral OCR service not available"):
                service.extract_text("/fake/path.png", 'png')

    def test_get_usage_info(self, mistral_service):
        """Test the get_usage_info method."""
        usage_info = mistral_service.get_usage_info()
        assert usage_info["provider"] == "mistral"
        assert usage_info["model"] == "mistral-ocr-latest"
        assert usage_info["available"] is True