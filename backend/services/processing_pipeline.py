"""
Processing Pipeline Module

Handles the document processing workflow including OCR extraction, AI analysis,
and results persistence with progress tracking.
"""

import logging
import asyncio
from typing import Dict, Optional

from models.health_models import HealthInsights
from services.database_manager import DatabaseManager
from services.mistral_ocr_service import MistralOCRService
from services.extraction_agent import ExtractionAgent
from services.insight_agent import InsightAgent

logger = logging.getLogger(__name__)


# Processing stages constants
class ProcessingStage:
    """Document processing stage constants for consistent stage tracking"""
    OCR_EXTRACTION = "ocr_extraction"
    AI_ANALYSIS = "ai_analysis"
    SAVING_RESULTS = "saving_results"
    COMPLETE = "complete"


# Progress percentages for each stage
STAGE_PROGRESS = {
    ProcessingStage.OCR_EXTRACTION: 10,
    ProcessingStage.AI_ANALYSIS: 50,
    ProcessingStage.SAVING_RESULTS: 90,
    ProcessingStage.COMPLETE: 100
}


class ProcessingPipeline:
    """
    Manages the document processing pipeline from OCR to final analysis.
    
    Coordinates between OCR extraction, AI analysis agents, and database persistence
    with comprehensive progress tracking and error handling.
    """
    
    def __init__(self, database_manager: DatabaseManager):
        """
        Initialize processing pipeline with required dependencies.
        
        Args:
            database_manager: Database manager for persistence operations
        """
        self.db_manager = database_manager
        self.ocr_agent = MistralOCRService()
        self.extraction_agent = ExtractionAgent()
        self.insight_agent = InsightAgent()
    
    async def process_document_async(self, document_id: str, file_url: str, filename: str) -> None:
        """
        Process document through complete pipeline asynchronously.
        
        Executes the full processing workflow:
        1. OCR text extraction
        2. AI data extraction and analysis  
        3. Results persistence
        4. Progress tracking throughout
        
        Args:
            document_id: Unique identifier for the document
            file_url: URL to the document file
            filename: Original filename for context
        """
        try:
            logger.info(f"🚀 Starting async processing pipeline for document {document_id}")
            
            # Stage 1: OCR Extraction
            structured_ocr_data = await self._execute_ocr_stage(document_id, file_url)
            
            # Stage 2: AI Analysis (Data Extraction + Insights)
            insights_result = await self._execute_analysis_stage(document_id, structured_ocr_data)
            
            # Stage 3: Save Results
            await self._execute_save_stage(document_id, filename, structured_ocr_data, insights_result)
            
            logger.info(f"✅ Successfully completed processing pipeline for document {document_id}")
            
        except Exception as e:
            logger.error(f"❌ Processing pipeline failed for document {document_id}: {e}", exc_info=True)
            self.db_manager.mark_document_error(document_id, str(e))
            raise
    
    async def _execute_ocr_stage(self, document_id: str, file_url: str) -> Dict:
        """
        Execute OCR extraction stage with progress tracking.
        
        Args:
            document_id: ID of the document being processed
            file_url: URL to the document file
            
        Returns:
            Dict: The structured JSON response from the OCR service.
            
        Raises:
            ValueError: If OCR extraction yields no data
        """
        logger.info(f"📄 Stage 1/4: Starting OCR extraction for {document_id}")
        self.db_manager.update_processing_stage(document_id, ProcessingStage.OCR_EXTRACTION)
        
        structured_ocr_data = self.ocr_agent.extract_structured_data(file_url)
        if not structured_ocr_data or not structured_ocr_data.get('pages'):
            raise ValueError("OCR process yielded no pages or data")
        
        # Log raw text for debugging purposes
        raw_text_for_db = "".join([page.get('markdown', '') for page in structured_ocr_data.get('pages', [])])
        self.db_manager.update_document_raw_text(document_id, raw_text_for_db)

        logger.info(f"✅ OCR extraction completed for {document_id}")
        return structured_ocr_data
    
    async def _execute_analysis_stage(self, document_id: str, structured_ocr_data: Dict) -> HealthInsights:
        """
        Execute AI analysis stage with progress tracking.
        
        Args:
            document_id: ID of the document being processed
            structured_ocr_data: The structured JSON response from the OCR service.
            
        Returns:
            HealthInsights: Structured health insights from AI analysis
        """
        # Stage 2a: Data Extraction
        logger.info(f"🧠 Stage 2a/4: Starting Data Extraction for {document_id}")
        self.db_manager.update_processing_stage(
            document_id, 
            ProcessingStage.AI_ANALYSIS, 
            {"progress": 30}
        )
        
        extracted_data = await self.extraction_agent.extract_data(structured_ocr_data)
        if not extracted_data.markers:
            logger.warning(f"ExtractionAgent returned no markers for document {document_id}")
        
        # Stage 2b: Insight Generation
        logger.info(f"🧠 Stage 2b/4: Starting Insight Generation for {document_id}")
        self.db_manager.update_processing_stage(document_id, ProcessingStage.AI_ANALYSIS, {"progress": 50})
        
        insights_result = await self.insight_agent.generate_insights(extracted_data)
        
        logger.info(f"✅ AI analysis completed for {document_id}")
        return insights_result
    
    async def _execute_save_stage(self, document_id: str, filename: str, structured_ocr_data: Dict, insights_result: HealthInsights) -> None:
        """
        Execute save results stage with progress tracking.
        
        Args:
            document_id: ID of the document being processed
            filename: Original filename of the document
            structured_ocr_data: The structured JSON response from the OCR service.
            insights_result: Health insights from AI analysis
        """
        logger.info(f"💾 Stage 3/4: Saving analysis results for {document_id}")
        self.db_manager.update_processing_stage(document_id, ProcessingStage.SAVING_RESULTS)
        
        # Add brief delay for stage visibility
        await asyncio.sleep(0.5)

        # For debugging, we still save the raw text, but the insights are generated from structured data
        raw_text = "".join([page.get('markdown', '') for page in structured_ocr_data.get('pages', [])])
        
        # Save complete results
        final_data = {
            "id": document_id,
            "filename": filename,
            "status": "complete",
            "raw_text": raw_text,
            "analysis": insights_result.model_dump(mode='json'),
            "progress": STAGE_PROGRESS[ProcessingStage.COMPLETE],
            "processing_stage": ProcessingStage.COMPLETE
        }
        
        # Save to database
        self._save_document_data(document_id, final_data)
        
        logger.info(f"✅ Results saved for {document_id}")
    
    def _save_document_data(self, document_id: str, data: Dict) -> None:
        """
        Save document data with analysis results.
        
        Args:
            document_id: ID of the document
            data: Complete document data including analysis
        """
        try:
            # Update main document table
            self.db_manager.update_document_table(document_id, data)
            
            # Save analysis results if available
            if "analysis" in data and data["analysis"]:
                self.db_manager.save_analysis_results(document_id, data["analysis"])
                
            logger.info(f"Document data saved successfully for {document_id}")
            
        except Exception as e:
            logger.error(f"Error saving document data for {document_id}: {e}", exc_info=True)
            self.db_manager.mark_document_error(document_id, str(e))
            raise
    
    async def retry_processing(self, document_id: str) -> bool:
        """
        Retry processing for a stuck or failed document.
        
        Resets the document status and restarts the processing pipeline.
        This is useful when documents get stuck in processing or fail.
        
        Args:
            document_id: ID of document to retry
            
        Returns:
            bool: True if retry was initiated, False if document not found or already complete
        """
        try:
            document_data = self.db_manager.load_document_data(document_id)
            if not document_data:
                logger.warning(f"Document {document_id} not found for retry")
                return False
            
            # Don't retry already completed documents
            if document_data.get("status") == "complete":
                logger.info(f"Document {document_id} is already complete, skipping retry")
                return False
            
            logger.info(f"🔄 Retrying processing for document {document_id}")
            
            # Reset document status to processing with initial stage
            reset_data = {
                "status": "processing",
                "progress": 0,
                "processing_stage": ProcessingStage.OCR_EXTRACTION,
                "error_message": None
            }
            
            self.db_manager.update_document_table(document_id, reset_data)
            
            # Restart the processing pipeline
            file_url = document_data.get("public_url")
            filename = document_data.get("filename", "unknown")
            
            if file_url:
                # Start async processing
                asyncio.create_task(self.process_document_async(document_id, file_url, filename))
                logger.info(f"✅ Retry processing initiated for document {document_id}")
                return True
            else:
                logger.error(f"No file URL found for document {document_id}, cannot retry")
                return False
                
        except Exception as e:
            logger.error(f"Error retrying processing for document {document_id}: {e}", exc_info=True)
            return False