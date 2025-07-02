import os
import aiofiles
from fastapi import UploadFile
import uuid
from typing import List
import logging

logger = logging.getLogger(__name__)

class FileHandler:
    """Handle file upload and validation"""
    
    def __init__(self):
        self.upload_dir = "uploads"
        self.max_file_size = 10 * 1024 * 1024  # 10MB
        self.allowed_extensions = {'.pdf', '.png', '.jpg', '.jpeg'}
        self.ensure_upload_directory()
    
    def ensure_upload_directory(self):
        """Ensure upload directory exists"""
        os.makedirs(self.upload_dir, exist_ok=True)
    
    def is_valid_file(self, file: UploadFile) -> bool:
        """Validate uploaded file"""
        try:
            # Check file size
            if hasattr(file, 'size') and file.size > self.max_file_size:
                return False
            
            # Check file extension
            if file.filename:
                file_ext = os.path.splitext(file.filename)[1].lower()
                if file_ext not in self.allowed_extensions:
                    return False
            
            # Check content type
            allowed_content_types = {
                'application/pdf',
                'image/png',
                'image/jpeg',
                'image/jpg'
            }
            
            if file.content_type not in allowed_content_types:
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"File validation error: {e}")
            return False
    
    async def save_upload(self, file: UploadFile) -> str:
        """Save uploaded file and return file path"""
        try:
            # Generate unique filename
            file_id = str(uuid.uuid4())
            file_ext = os.path.splitext(file.filename)[1].lower()
            filename = f"{file_id}{file_ext}"
            file_path = os.path.join(self.upload_dir, filename)
            
            # Save file
            async with aiofiles.open(file_path, 'wb') as f:
                content = await file.read()
                await f.write(content)
            
            logger.info(f"File saved: {file_path}")
            return file_path
            
        except Exception as e:
            logger.error(f"File save error: {e}")
            raise Exception(f"Failed to save file: {str(e)}")
    
    def delete_file(self, file_path: str) -> bool:
        """Delete a file"""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                return True
            return False
        except Exception as e:
            logger.error(f"File deletion error: {e}")
            return False
    
    def get_file_type(self, filename: str) -> str:
        """Get file type from filename"""
        return os.path.splitext(filename)[1].lower().lstrip('.')