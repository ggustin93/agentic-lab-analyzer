import pytesseract
from PIL import Image
import PyPDF2
import io
import logging
from typing import Optional
import os

logger = logging.getLogger(__name__)

class OCRService:
    """Service for extracting text from images and PDFs"""
    
    def __init__(self):
        self.tesseract_available = self._check_tesseract()
    
    def _check_tesseract(self) -> bool:
        """Check if Tesseract is available"""
        try:
            pytesseract.get_tesseract_version()
            return True
        except Exception as e:
            logger.warning(f"Tesseract not available: {e}")
            return False
    
    def is_available(self) -> bool:
        """Check if OCR service is available"""
        return self.tesseract_available
    
    async def extract_text_from_image(self, image_path: str) -> str:
        """Extract text from an image file"""
        try:
            if not self.tesseract_available:
                raise Exception("Tesseract OCR not available")
            
            # Open and process image
            with Image.open(image_path) as image:
                # Convert to RGB if necessary
                if image.mode != 'RGB':
                    image = image.convert('RGB')
                
                # Extract text using Tesseract
                text = pytesseract.image_to_string(
                    image,
                    config='--oem 3 --psm 6'  # OCR Engine Mode 3, Page Segmentation Mode 6
                )
                
                return text.strip()
                
        except Exception as e:
            logger.error(f"OCR extraction error: {e}")
            raise Exception(f"Failed to extract text from image: {str(e)}")
    
    async def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract text from a PDF file"""
        try:
            text_content = []
            
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                
                for page_num, page in enumerate(pdf_reader.pages):
                    try:
                        page_text = page.extract_text()
                        if page_text.strip():
                            text_content.append(f"--- Page {page_num + 1} ---\n{page_text}")
                    except Exception as e:
                        logger.warning(f"Failed to extract text from page {page_num + 1}: {e}")
                        continue
            
            if not text_content:
                raise Exception("No text could be extracted from PDF")
            
            return "\n\n".join(text_content)
            
        except Exception as e:
            logger.error(f"PDF extraction error: {e}")
            raise Exception(f"Failed to extract text from PDF: {str(e)}")
    
    async def extract_text(self, file_path: str, file_type: str) -> str:
        """Extract text from file based on type"""
        try:
            if file_type.lower() == 'pdf':
                return await self.extract_text_from_pdf(file_path)
            elif file_type.lower() in ['png', 'jpg', 'jpeg']:
                return await self.extract_text_from_image(file_path)
            else:
                raise Exception(f"Unsupported file type: {file_type}")
                
        except Exception as e:
            logger.error(f"Text extraction error: {e}")
            raise
    
    def preprocess_image(self, image_path: str) -> str:
        """Preprocess image for better OCR results"""
        try:
            with Image.open(image_path) as image:
                # Convert to grayscale
                if image.mode != 'L':
                    image = image.convert('L')
                
                # Enhance contrast and sharpness if needed
                # This is a basic implementation - could be enhanced
                
                # Save preprocessed image
                preprocessed_path = image_path.replace('.', '_preprocessed.')
                image.save(preprocessed_path)
                
                return preprocessed_path
                
        except Exception as e:
            logger.error(f"Image preprocessing error: {e}")
            return image_path  # Return original if preprocessing fails