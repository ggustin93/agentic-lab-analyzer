"""
Mistral OCR Service Implementation
Provides cloud-based OCR using Mistral's OCR API
"""

import os
import base64
import logging
import magic
import requests
from typing import Dict, Any

from config.settings import settings

logger = logging.getLogger(__name__)

class MistralOCRService:
    """Mistral OCR service for cloud-based text extraction using direct HTTP requests."""

    def __init__(self):
        """Initializes the Mistral OCR Service."""
        self.api_key = settings.MISTRAL_API_KEY
        self.model = "mistral-ocr-latest"
        self.api_url = "https://api.mistral.ai/v1/ocr"
        self.headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        if not self.api_key:
            logger.warning("MISTRAL_API_KEY not set. Mistral OCR service will be disabled.")
        else:
            logger.info("Mistral OCR service initialized and available.")

    def is_available(self) -> bool:
        """Check if Mistral OCR service is available."""
        return bool(self.api_key)

    def extract_text(self, file_path: str, file_type: str) -> str:
        """
        Extracts text from a given file (image or PDF) using Mistral's OCR API.
        """
        if not self.is_available():
            raise Exception("Mistral OCR service not available. MISTRAL_API_KEY is not set.")

        filename = os.path.basename(file_path)
        logger.info(f"Starting OCR extraction for: {filename}")

        try:
            with open(file_path, "rb") as f:
                content = f.read()
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

            response = requests.post(self.api_url, headers=self.headers, json=payload, timeout=120)
            response.raise_for_status()

            ocr_result = response.json()
            logger.debug(f"Mistral OCR API full response: {ocr_result}")  # Log the full response
            
            # The API returns a list of pages, each with a 'markdown' field.
            # We concatenate the text from all pages, adding a separator.
            pages_text = []
            for page in ocr_result.get('pages', []):
                page_index = page.get('index', 'N/A')
                markdown_text = page.get('markdown', '')
                pages_text.append(f"--- Page {page_index + 1} ---\n\n{markdown_text}\n\n")
            
            extracted_text = "".join(pages_text)

            if not extracted_text:
                 logger.warning(f"OCR for {filename} completed but no text was extracted.")
                 return ""
            
            logger.info(f"Successfully extracted {len(extracted_text)} characters from {filename}.")
            return extracted_text

        except requests.exceptions.RequestException as e:
            logger.error(f"HTTP request failed during OCR for {filename}: {e}", exc_info=True)
            raise Exception(f"Failed to process {filename} due to a network error: {e}")
        except Exception as e:
            logger.error(f"An unexpected error occurred during OCR for {filename}: {e}", exc_info=True)
            raise Exception(f"An unexpected error occurred while processing {filename}: {e}")

    def get_usage_info(self) -> Dict[str, Any]:
        """Get usage information for monitoring."""
        return {
            "provider": "mistral",
            "model": self.model,
            "available": self.is_available(),
            "supported_formats": [".pdf", ".jpg", ".jpeg", ".png"]
        }