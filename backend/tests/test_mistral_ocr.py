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
def mock_requests():
    """Mock requests module"""
    with patch('services.mistral_ocr_service.requests') as mock_requests:
        yield mock_requests

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

    def test_extract_text_from_image_success(self, mistral_service, mock_requests, tmp_path):
        """Test successful text extraction from an image."""
        # Mock the GET request to download the file
        mock_get_response = MagicMock()
        mock_get_response.status_code = 200
        mock_get_response.content = b"fake image content"
        mock_requests.get.return_value = mock_get_response
        
        # Mock the POST request to Mistral API
        mock_post_response = MagicMock()
        mock_post_response.status_code = 200
        mock_post_response.json.return_value = {
            "pages": [{"index": 0, "markdown": "Extracted text from image."}]
        }
        mock_requests.post.return_value = mock_post_response
        
        # Mock magic.from_buffer to return an image MIME type
        with patch('services.mistral_ocr_service.magic.from_buffer') as mock_magic:
            mock_magic.return_value = "image/png"
            
            result = mistral_service.extract_structured_data("http://example.com/test.png")
            assert result["pages"][0]["markdown"] == "Extracted text from image."
            mock_requests.get.assert_called_once()
            mock_requests.post.assert_called_once()

    def test_extract_text_from_pdf_success(self, mistral_service, mock_requests, tmp_path):
        """Test successful text extraction from a PDF."""
        # Mock the GET request to download the file
        mock_get_response = MagicMock()
        mock_get_response.status_code = 200
        mock_get_response.content = b"%PDF-1.4\n1 0 obj<</Type/Catalog/Pages 2 0 R>>endobj\n"
        mock_requests.get.return_value = mock_get_response
        
        # Mock the POST request to Mistral API
        mock_post_response = MagicMock()
        mock_post_response.status_code = 200
        mock_post_response.json.return_value = {
            "pages": [{"index": 0, "markdown": "Extracted text from PDF."}]
        }
        mock_requests.post.return_value = mock_post_response
        
        # Mock magic.from_buffer to return a PDF MIME type
        with patch('services.mistral_ocr_service.magic.from_buffer') as mock_magic:
            mock_magic.return_value = "application/pdf"
            
            result = mistral_service.extract_structured_data("http://example.com/test.pdf")
            assert result["pages"][0]["markdown"] == "Extracted text from PDF."
            mock_requests.get.assert_called_once()
            mock_requests.post.assert_called_once()
        
    def test_extract_text_service_unavailable(self):
        """Test extraction when service is unavailable."""
        with patch('services.mistral_ocr_service.settings.MISTRAL_API_KEY', new=''):
            service = MistralOCRService()
            with pytest.raises(Exception, match="Mistral OCR service not available"):
                service.extract_structured_data("http://example.com/fake.png")

    def test_get_usage_info(self, mistral_service):
        """Test the get_usage_info method."""
        usage_info = mistral_service.get_usage_info()
        assert usage_info["provider"] == "mistral"
        assert usage_info["model"] == "mistral-ocr-latest"
        assert usage_info["available"] is True