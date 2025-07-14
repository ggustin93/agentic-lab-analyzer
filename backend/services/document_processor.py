"""
Document Processor - Refactored Version

Main orchestrator for document processing workflow. 
Clean, focused implementation using separate managers for different concerns.
"""

import asyncio
import uuid
import os
import logging
from typing import Dict, List, Optional

from supabase import create_client, Client

from config.settings import settings
from services.storage_manager import StorageManager
from services.database_manager import DatabaseManager
from services.processing_pipeline import ProcessingPipeline

logger = logging.getLogger(__name__)


class DocumentProcessor:
    """
    Main service for processing health documents through OCR and AI analysis pipeline.
    
    Refactored to use specialized managers for different concerns:
    - StorageManager: File upload/deletion operations
    - DatabaseManager: All database operations
    - ProcessingPipeline: OCR + AI analysis workflow
    
    This provides clean separation of concerns and improved maintainability.
    """
    
    def __init__(self):
        """Initialize the document processor with required managers."""
        # Initialize Supabase client
        self.supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        
        # Initialize specialized managers
        self.storage_manager = StorageManager(self.supabase)
        self.database_manager = DatabaseManager(self.supabase)
        self.processing_pipeline = ProcessingPipeline(self.database_manager)
    
    # === PUBLIC API METHODS ===
    
    async def process_document(self, file_content: bytes, filename: str) -> str:
        """
        Process a document and return document ID for tracking.
        
        Args:
            file_content: Binary content of the uploaded file
            filename: Original filename from upload
            
        Returns:
            str: Document ID for tracking processing status
            
        Raises:
            Exception: If upload or initial processing fails
        """
        document_id = str(uuid.uuid4())
        file_extension = os.path.splitext(filename)[1]
        storage_path = f"{document_id}{file_extension}"

        try:
            # Upload to storage and create initial record
            public_url = self.storage_manager.upload_file(file_content, storage_path)
            self.database_manager.create_document_record(document_id, filename, storage_path, public_url)

            # Start async processing pipeline
            asyncio.create_task(
                self.processing_pipeline.process_document_async(document_id, public_url, filename)
            )
            
            logger.info(f"Document {document_id} queued for processing")
            return document_id
            
        except Exception as e:
            logger.error(f"Document processing error for {document_id}: {e}", exc_info=True)
            self.database_manager.mark_document_error(document_id, str(e))
            raise
    
    async def delete_document(self, document_id: str) -> bool:
        """
        Delete a document and all associated data with improved error handling.
        
        Implements a resilient deletion process that handles various failure scenarios:
        - Partial deletion recovery
        - Storage file cleanup retries
        - Database constraint handling
        - Detailed error logging
        
        Args:
            document_id: ID of document to delete
            
        Returns:
            bool: True if deletion successful, False if document not found or deletion failed
        """
        max_retries = 3
        retry_delay = 1.0
        
        for attempt in range(max_retries):
            try:
                document_data = self.database_manager.load_document_data(document_id)
                if not document_data:
                    logger.warning(f"Document {document_id} not found for deletion")
                    return False

                logger.info(f"Starting deletion attempt {attempt + 1}/{max_retries} for document {document_id}")

                # Step 1: Delete analysis data (handles foreign key constraints)
                try:
                    await self.database_manager.delete_analysis_data(document_id)
                    logger.info(f"Successfully deleted analysis data for document {document_id}")
                except Exception as e:
                    logger.warning(f"Analysis data deletion failed for {document_id}: {e}")
                    if attempt == max_retries - 1:
                        # If this is the last attempt, continue anyway as analysis data might not exist
                        logger.info(f"Continuing deletion despite analysis data error on final attempt")

                # Step 2: Delete storage file (with retry logic)
                storage_path = document_data.get("storage_path")
                if storage_path:
                    try:
                        await self.storage_manager.delete_file_with_retry(storage_path)
                        logger.info(f"Successfully deleted storage file for document {document_id}")
                    except Exception as e:
                        logger.warning(f"Storage file deletion failed for {document_id}: {e}")
                        if attempt == max_retries - 1:
                            # Continue with document record deletion even if storage file fails
                            logger.warning(f"Continuing deletion despite storage file error on final attempt")

                # Step 3: Delete document record (most critical step)
                try:
                    self.database_manager.delete_document_record(document_id)
                    logger.info(f"Successfully deleted document record for {document_id}")
                    
                    # If we reach here, deletion was successful
                    logger.info(f"Successfully deleted document {document_id} on attempt {attempt + 1}")
                    return True
                    
                except Exception as e:
                    logger.error(f"Critical: Document record deletion failed for {document_id}: {e}")
                    if attempt < max_retries - 1:
                        logger.info(f"Retrying deletion in {retry_delay} seconds...")
                        await asyncio.sleep(retry_delay)
                        retry_delay *= 2  # Exponential backoff
                        continue
                    else:
                        # Final attempt failed
                        logger.error(f"All deletion attempts failed for document {document_id}")
                        return False

            except Exception as e:
                logger.error(f"Unexpected error during deletion attempt {attempt + 1} for document {document_id}: {e}", exc_info=True)
                if attempt < max_retries - 1:
                    logger.info(f"Retrying deletion in {retry_delay} seconds...")
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2
                    continue
                else:
                    logger.error(f"All deletion attempts failed for document {document_id}")
                    return False

        return False
    
    async def retry_document_processing(self, document_id: str) -> bool:
        """
        Retry processing for a stuck or failed document.
        
        Args:
            document_id: ID of document to retry
            
        Returns:
            bool: True if retry was initiated, False if document not found or cannot be retried
        """
        return await self.processing_pipeline.retry_processing(document_id)
    
    async def list_documents(self) -> List[Dict]:
        """
        List all processed documents.
        
        Returns:
            List[Dict]: Array of document data formatted for frontend
        """
        try:
            return await self.database_manager.list_documents()
        except Exception as e:
            logger.error(f"List documents error: {str(e)}")
            raise
    
    def get_analysis(self, document_id: str) -> Optional[Dict]:
        """
        Get a specific document by ID with analysis results.
        
        Args:
            document_id: ID of the document to retrieve
            
        Returns:
            Optional[Dict]: Document analysis data or None if not found
        """
        try:
            return self.database_manager.get_analysis(document_id)
        except Exception as e:
            logger.error(f"Get document error: {str(e)}")
            return None