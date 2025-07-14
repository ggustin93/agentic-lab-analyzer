"""
Storage Manager Module

Handles all file storage operations for documents including upload, deletion, and retry logic.
Provides clean separation of storage concerns from business logic.
"""

import logging
import asyncio
from typing import Optional
from supabase import Client

from config.settings import settings

logger = logging.getLogger(__name__)


class StorageManager:
    """
    Manages file storage operations with Supabase storage.
    
    Provides robust file upload and deletion capabilities with retry logic
    for handling transient storage errors.
    """
    
    def __init__(self, supabase_client: Client):
        """
        Initialize storage manager with Supabase client.
        
        Args:
            supabase_client: Configured Supabase client instance
        """
        self.supabase = supabase_client
        self.bucket_name = settings.SUPABASE_BUCKET_NAME
    
    def upload_file(self, file_content: bytes, storage_path: str) -> str:
        """
        Upload file to Supabase storage and return public URL.
        
        Args:
            file_content: Binary content of the file
            storage_path: Path where the file will be stored
            
        Returns:
            str: Public URL to access the uploaded file
            
        Raises:
            Exception: If upload fails
        """
        try:
            self.supabase.storage.from_(self.bucket_name).upload(
                path=storage_path,
                file=file_content,
                file_options={"cache-control": "3600", "content-type": "application/pdf"}
            )
            public_url = self.supabase.storage.from_(self.bucket_name).get_public_url(storage_path)
            logger.info(f"Successfully uploaded file to storage: {storage_path}")
            return public_url
        except Exception as e:
            logger.error(f"Failed to upload file to storage: {storage_path}, error: {e}")
            raise
    
    async def delete_file(self, storage_path: Optional[str]) -> None:
        """
        Delete file from storage if path exists.
        
        Args:
            storage_path: Path to the file in storage
        """
        if not storage_path:
            return
            
        try:
            self.supabase.storage.from_(self.bucket_name).remove([storage_path])
            logger.info(f"Successfully deleted file from storage: {storage_path}")
        except Exception as e:
            logger.warning(f"Failed to delete storage file {storage_path}: {e}")
    
    async def delete_file_with_retry(self, storage_path: str, max_retries: int = 3) -> None:
        """
        Delete file from storage with retry logic for resilience.
        
        Args:
            storage_path: Path to the file in storage
            max_retries: Maximum number of retry attempts
            
        Raises:
            Exception: If all retry attempts fail
        """
        retry_delay = 1.0
        
        for attempt in range(max_retries):
            try:
                self.supabase.storage.from_(self.bucket_name).remove([storage_path])
                logger.info(f"Successfully deleted file from storage: {storage_path}")
                return
            except Exception as e:
                if attempt < max_retries - 1:
                    logger.warning(f"Storage file deletion attempt {attempt + 1} failed for {storage_path}: {e}")
                    logger.info(f"Retrying storage file deletion in {retry_delay} seconds...")
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                else:
                    logger.error(f"All storage file deletion attempts failed for {storage_path}: {e}")
                    raise