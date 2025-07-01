"""
Mistral OCR Service Implementation
Provides cloud-based OCR using Mistral's OCR API
"""

import os
import base64
import logging
from typing import Optional, Dict, Any
from io import BytesIO
from PIL import Image

try:
    from mistralai import Mistral
    MISTRAL_AVAILABLE = True
except ImportError:
    MISTRAL_AVAILABLE = False
    logging.warning("Mistral AI not available - install with: pip install mistralai")

from config.settings import settings

logger = logging.getLogger(__name__)

class MistralOCRService:
    """Mistral OCR service for cloud-based text extraction"""
    
    def __init__(self):
        self.api_key = settings.mistral_api_key
        self.model = settings.mistral_ocr_model
        self.client = None
        
        if MISTRAL_AVAILABLE and self.api_key:
            self.client = Mistral(api_key=self.api_key)
        
        # Valid file extensions
        self.valid_document_extensions = {".pdf"}
        self.valid_image_extensions = {".jpg", ".jpeg", ".png"}
    
    def is_available(self) -> bool:
        """Check if Mistral OCR service is available"""
        return MISTRAL_AVAILABLE and self.client is not None and self.api_key is not None
    
    async def extract_text_from_image(self, image_path: str) -> str:
        """Extract text from an image using Mistral OCR"""
        try:
            if not self.is_available():
                raise Exception("Mistral OCR service not available")
            
            # Load and encode image
            with Image.open(image_path) as img:
                # Convert to PNG format for consistency
                buffered = BytesIO()
                img.save(buffered, format="PNG")
                img_str = base64.b64encode(buffered.getvalue()).decode()
                
                # Create document source
                document_source = {
                    "type": "image_url",
                    "image_url": f"data:image/png;base64,{img_str}"
                }
                
                # Process OCR
                ocr_response = self.client.ocr.process(
                    model=self.model,
                    document=document_source,
                    include_image_base64=False  # We don't need images back
                )
                
                # Extract text from all pages
                extracted_text = "\n\n".join(
                    page.markdown for page in ocr_response.pages
                )
                
                return extracted_text.strip()
                
        except Exception as e:
            logger.error(f"Mistral OCR extraction error: {e}")
            raise Exception(f"Failed to extract text from image: {str(e)}")
    
    async def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from a PDF using Mistral OCR"""
        try:
            if not self.is_available():
                raise Exception("Mistral OCR service not available")
            
            # Upload PDF to Mistral
            with open(pdf_path, "rb") as f:
                content = f.read()
            
            filename = os.path.basename(pdf_path)
            uploaded_file = self.client.files.upload(
                file={"file_name": filename, "content": content},
                purpose="ocr",
            )
            
            # Get signed URL
            signed_url = self.client.files.get_signed_url(file_id=uploaded_file.id)
            
            # Create document source
            document_source = {
                "type": "document_url",
                "document_url": signed_url.url
            }
            
            # Process OCR
            ocr_response = self.client.ocr.process(
                model=self.model,
                document=document_source,
                include_image_base64=False
            )
            
            # Extract text from all pages
            extracted_text = "\n\n".join(
                f"--- Page {i+1} ---\n{page.markdown}"
                for i, page in enumerate(ocr_response.pages)
            )
            
            return extracted_text.strip()
            
        except Exception as e:
            logger.error(f"Mistral PDF OCR error: {e}")
            raise Exception(f"Failed to extract text from PDF: {str(e)}")
    
    async def extract_text(self, file_path: str, file_type: str) -> str:
        """Extract text from file based on type"""
        try:
            file_extension = f".{file_type.lower()}"
            
            if file_extension == '.pdf':
                return await self.extract_text_from_pdf(file_path)
            elif file_extension in self.valid_image_extensions:
                return await self.extract_text_from_image(file_path)
            else:
                raise Exception(f"Unsupported file type: {file_type}")
                
        except Exception as e:
            logger.error(f"Mistral OCR text extraction error: {e}")
            raise
    
    def get_usage_info(self) -> Dict[str, Any]:
        """Get usage information for monitoring"""
        return {
            "provider": "mistral",
            "model": self.model,
            "available": self.is_available(),
            "supported_formats": list(self.valid_document_extensions | self.valid_image_extensions)
        }