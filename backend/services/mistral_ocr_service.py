"""
Mistral OCR Service Implementation
Provides cloud-based OCR using Mistral's OCR API.

Fully async (httpx): OCR calls run for up to two minutes, and a synchronous
client here would block the whole event loop for that time (backlog 009).
"""

import base64
import logging
import magic
import httpx
from typing import Dict, Any

from config.settings import settings

logger = logging.getLogger(__name__)


class MistralOCRService:
    """Mistral OCR service for cloud-based text extraction."""

    def __init__(self):
        """Initializes the Mistral OCR Service."""
        self.api_key = settings.MISTRAL_API_KEY
        self.model = settings.MISTRAL_OCR_MODEL
        self.api_url = "https://api.mistral.ai/v1/ocr"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        self.client = httpx.AsyncClient(timeout=httpx.Timeout(120.0, connect=30.0))
        if not self.api_key:
            logger.warning("MISTRAL_API_KEY not set. Mistral OCR service will be disabled.")
        else:
            logger.info("Mistral OCR service initialized and available.")

    def is_available(self) -> bool:
        """Check if Mistral OCR service is available."""
        return bool(self.api_key)

    async def extract_structured_data(self, file_url: str) -> Dict[str, Any]:
        """
        Extracts structured data from a given file URL using Mistral's OCR API.

        Returns the full JSON response, preserving the markdown structure for
        more intelligent parsing downstream.
        """
        if not self.is_available():
            raise Exception("Mistral OCR service not available. MISTRAL_API_KEY is not set.")

        filename = file_url.split('/')[-1].split('?')[0]
        logger.info(f"Starting OCR extraction for: {filename}")

        try:
            # Download the file content from the URL
            response = await self.client.get(file_url, timeout=30)
            response.raise_for_status()
            content = response.content

            base64_encoded_content = base64.b64encode(content).decode('utf-8')

            mime_type = magic.from_buffer(content, mime=True)
            logger.debug(f"Detected MIME type for {filename}: {mime_type}")

            data_url = f"data:{mime_type};base64,{base64_encoded_content}"

            if "pdf" in mime_type:
                document_data = {"type": "document_url", "document_url": data_url}
            elif "image" in mime_type:
                document_data = {"type": "image_url", "image_url": data_url}
            else:
                raise Exception(f"Unsupported MIME type: {mime_type}")

            payload = {
                "model": self.model,
                "document": document_data,
                "include_image_base64": False
            }

            response = await self.client.post(self.api_url, headers=self.headers, json=payload)
            response.raise_for_status()

            ocr_result = response.json()
            # Never log the response body: it contains the document's medical content
            logger.debug(f"Mistral OCR returned {len(ocr_result.get('pages', []))} page(s) for {filename}")

            if not ocr_result.get('pages'):
                logger.warning(f"OCR for {filename} completed but no pages were extracted.")
                return {}

            logger.info(f"Successfully extracted structured data from {filename}.")
            return ocr_result

        except httpx.HTTPError as e:
            logger.error(f"HTTP request failed during OCR for {filename}: {e}", exc_info=True)
            raise Exception(f"Failed to process {filename} due to a network error: {e}")
        except Exception as e:
            logger.error(f"An unexpected error occurred during OCR for {filename}: {e}", exc_info=True)
            raise Exception(f"An unexpected error occurred while processing {filename}: {e}")

    async def close(self):
        """Close the underlying HTTP client (called from the app lifespan)."""
        await self.client.aclose()

    def get_usage_info(self) -> Dict[str, Any]:
        """Get usage information for monitoring."""
        return {
            "provider": "mistral",
            "model": self.model,
            "available": self.is_available(),
            "supported_formats": [".pdf", ".jpg", ".jpeg", ".png"]
        }
