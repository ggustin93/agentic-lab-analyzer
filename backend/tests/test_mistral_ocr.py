"""
Tests for Mistral OCR service (async httpx client, mocked).
"""

import pytest
from unittest.mock import patch, MagicMock, AsyncMock

from services.mistral_ocr_service import MistralOCRService


@pytest.fixture
def mistral_service():
    """Service with its HTTP client replaced by async mocks."""
    service = MistralOCRService()
    service.client = MagicMock()
    service.client.get = AsyncMock()
    service.client.post = AsyncMock()
    service.client.aclose = AsyncMock()
    return service


def _response(status_code=200, content=b"", json_data=None):
    response = MagicMock()
    response.status_code = status_code
    response.content = content
    response.json.return_value = json_data or {}
    response.raise_for_status.return_value = None
    return response


class TestMistralOCRService:
    """Test suite for the MistralOCRService."""

    def test_is_available_with_key(self, mistral_service):
        """The service is available when an API key is provided."""
        assert mistral_service.is_available() is True

    def test_is_available_without_key(self):
        """The service is unavailable when the API key is missing."""
        with patch('services.mistral_ocr_service.settings.MISTRAL_API_KEY', new=''):
            service = MistralOCRService()
            assert service.is_available() is False

    @pytest.mark.asyncio
    async def test_extract_text_from_image_success(self, mistral_service):
        """Successful structured extraction from an image URL."""
        mistral_service.client.get.return_value = _response(content=b"fake image content")
        mistral_service.client.post.return_value = _response(json_data={
            "pages": [{"index": 0, "markdown": "Extracted text from image."}]
        })

        with patch('services.mistral_ocr_service.magic.from_buffer', return_value="image/png"):
            result = await mistral_service.extract_structured_data("http://example.com/test.png")

        assert result["pages"][0]["markdown"] == "Extracted text from image."
        mistral_service.client.get.assert_called_once()
        mistral_service.client.post.assert_called_once()

    @pytest.mark.asyncio
    async def test_extract_text_from_pdf_success(self, mistral_service):
        """Successful structured extraction from a PDF URL."""
        mistral_service.client.get.return_value = _response(content=b"%PDF-1.4 fake")
        mistral_service.client.post.return_value = _response(json_data={
            "pages": [{"index": 0, "markdown": "Extracted text from PDF."}]
        })

        with patch('services.mistral_ocr_service.magic.from_buffer', return_value="application/pdf"):
            result = await mistral_service.extract_structured_data("http://example.com/test.pdf")

        assert result["pages"][0]["markdown"] == "Extracted text from PDF."

    @pytest.mark.asyncio
    async def test_extract_text_unsupported_mime_type(self, mistral_service):
        """A non-PDF, non-image payload is refused before any OCR call."""
        mistral_service.client.get.return_value = _response(content=b"plain text")

        with patch('services.mistral_ocr_service.magic.from_buffer', return_value="text/plain"):
            with pytest.raises(Exception, match="Unsupported MIME type"):
                await mistral_service.extract_structured_data("http://example.com/test.txt")

        mistral_service.client.post.assert_not_called()

    @pytest.mark.asyncio
    async def test_extract_text_service_unavailable(self):
        """Extraction fails fast when the service is unavailable."""
        with patch('services.mistral_ocr_service.settings.MISTRAL_API_KEY', new=''):
            service = MistralOCRService()
            with pytest.raises(Exception, match="Mistral OCR service not available"):
                await service.extract_structured_data("http://example.com/fake.png")
            await service.close()

    def test_get_usage_info(self, mistral_service):
        """Usage info reflects provider, model and availability."""
        usage_info = mistral_service.get_usage_info()
        assert usage_info["provider"] == "mistral"
        assert usage_info["model"] == "mistral-ocr-latest"
        assert usage_info["available"] is True
