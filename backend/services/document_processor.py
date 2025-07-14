import asyncio
import uuid
import os
import json
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import logging

from supabase import create_client, Client

from config.settings import settings
from models.document_models import Document, AnalysisResult, HealthMarkerDB
from models.health_models import HealthInsights
from agents.base import OCRExtractorAgent, LabInsightAgent
from .mistral_ocr_service import MistralOCRService
# Updated to use new specialized agents instead of the old monolithic ChutesAILabAgent 
# ADD the new agent imports
from .extraction_agent import ExtractionAgent
from .insight_agent import InsightAgent

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

class DocumentProcessor:
    """
    Main service for processing health documents through OCR and AI analysis pipeline.
    
    Handles the complete lifecycle: upload → OCR extraction → AI analysis → data persistence.
    Provides real-time progress tracking through 4-stage processing pipeline.
    """
    
    def __init__(self):
        """Initialize the document processor with OCR and AI analysis agents."""
        self.ocr_agent: OCRExtractorAgent = MistralOCRService()
        # REPLACE the single insight_agent with two specialized agents
        # self.insight_agent: LabInsightAgent = ChutesAILabAgent()
        self.extraction_agent = ExtractionAgent()
        self.insight_agent = InsightAgent()
        self.supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        self.bucket_name = settings.SUPABASE_BUCKET_NAME
    
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
            public_url = self._upload_to_storage(file_content, storage_path)
            self._create_document_record(document_id, filename, storage_path, public_url)

            # Start async processing pipeline
            asyncio.create_task(self._process_document_async(document_id, public_url, filename))
            
            return document_id
            
        except Exception as e:
            logger.error(f"Document processing error for {document_id}: {e}", exc_info=True)
            self._mark_document_error(document_id, str(e))
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
                document_data = self._load_document_data(document_id)
                if not document_data:
                    logger.warning(f"Document {document_id} not found for deletion")
                    return False

                logger.info(f"Starting deletion attempt {attempt + 1}/{max_retries} for document {document_id}")

                # Step 1: Delete analysis data (handles foreign key constraints)
                try:
                    await self._delete_analysis_data(document_id)
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
                        await self._delete_storage_file_with_retry(storage_path)
                        logger.info(f"Successfully deleted storage file for document {document_id}")
                    except Exception as e:
                        logger.warning(f"Storage file deletion failed for {document_id}: {e}")
                        if attempt == max_retries - 1:
                            # Continue with document record deletion even if storage file fails
                            logger.warning(f"Continuing deletion despite storage file error on final attempt")

                # Step 3: Delete document record (most critical step)
                try:
                    self._delete_document_record(document_id)
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
        
        Resets the document status and restarts the processing pipeline.
        This is useful when documents get stuck in processing or fail.
        
        Args:
            document_id: ID of document to retry
            
        Returns:
            bool: True if retry was initiated, False if document not found or already complete
        """
        try:
            document_data = self._load_document_data(document_id)
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
                "error_message": None,
                "processed_at": None
            }
            self._save_document_data(document_id, reset_data)
            
            # Clear any existing analysis results to start fresh
            await self._delete_analysis_data(document_id)
            
            # Get the public URL for reprocessing
            public_url = document_data.get("public_url")
            filename = document_data.get("filename")
            
            if not public_url or not filename:
                logger.error(f"Missing public_url or filename for document {document_id}")
                self._mark_document_error(document_id, "Missing file information for retry")
                return False
            
            # Start the processing pipeline again
            asyncio.create_task(self._process_document_async(document_id, public_url, filename))
            
            logger.info(f"✅ Successfully initiated retry for document {document_id}")
            return True

        except Exception as e:
            logger.error(f"Error retrying document {document_id}: {e}", exc_info=True)
            self._mark_document_error(document_id, f"Retry failed: {str(e)}")
            return False
    
    async def list_documents(self) -> List[Dict]:
        """
        Retrieve all documents with consistent date formatting for frontend.
        
        Returns:
            List[Dict]: Documents with standardized field names and date formats
        """
        try:
            result = self.supabase.table("documents").select(
                "id, filename, upload_date, status, processed_at, public_url"
            ).order("upload_date", desc=True).execute()
            
            documents = result.data if result.data else []
            return [self._format_document_for_frontend(doc) for doc in documents]
            
        except Exception as e:
            logger.error(f"Error listing documents: {e}")
            return []

    def get_analysis(self, document_id: str) -> Optional[Dict]:
        """
        Get comprehensive analysis data for a document, formatted for the frontend.
        
        Args:
            document_id: ID of document to retrieve
            
        Returns:
            Optional[Dict]: Formatted document data with analysis results, or None if not found
        """
        try:
            # 1. Fetch the base document
            doc_result = self.supabase.table("documents").select("*").eq("id", document_id).maybe_single().execute()
            if not doc_result.data:
                logger.warning(f"Document {document_id} not found in get_analysis")
                return None
            
            doc = self._format_document_for_frontend(doc_result.data)

            # 2. If complete, fetch and attach analysis results
            if doc.get("status") == "complete":
                analysis_result = self.supabase.table("analysis_results").select("*").eq(
                    "document_id", document_id
                ).maybe_single().execute()
                
                if analysis_result.data:
                    analysis_data = analysis_result.data
                    doc["processed_at"] = self._format_iso_date(analysis_data.get("created_at"))
                    doc["raw_text"] = analysis_data.get("raw_text") or doc_result.data.get("raw_text")
                    doc["ai_insights"] = analysis_data.get("insights")
                    
                    # Fetch and format health markers
                    markers_result = self.supabase.table("health_markers").select(
                        "marker_name, value, unit, reference_range"
                    ).eq("analysis_id", analysis_data['id']).execute()
                    
                    if markers_result.data:
                        doc["extracted_data"] = [
                            {
                                "marker": item["marker_name"],
                                "value": item["value"],
                                "unit": item["unit"],
                                "reference_range": item["reference_range"]
                            } for item in markers_result.data
                        ]
                        logger.info(f"Found {len(doc['extracted_data'])} markers for document {document_id}")
                    else:
                        doc["extracted_data"] = []
                else:
                    # Handle case where document is 'complete' but analysis record is missing
                    doc["extracted_data"] = []
                    doc["ai_insights"] = "Analysis data not found."
                    doc["raw_text"] = doc_result.data.get("raw_text")
            
            # Ensure keys exist even if not complete
            doc.setdefault("extracted_data", [])
            doc.setdefault("ai_insights", None)
            doc.setdefault("raw_text", None)

            return doc
            
        except Exception as e:
            logger.error(f"Error retrieving analysis for {document_id}: {e}", exc_info=True)
            return None
    
    # === PRIVATE PROCESSING METHODS ===
    
    async def _process_document_async(self, document_id: str, file_url: str, filename: str):
        """
        Execute the complete async processing pipeline with stage tracking.
        
        Pipeline: OCR Extraction → AI Analysis → Save Results → Complete
        
        Args:
            document_id: Unique identifier for the document
            file_url: Public URL to access the document
            filename: Original name of the uploaded file
        """
        try:
            document_data = self._load_document_data(document_id)
            if not document_data:
                logger.error(f"Could not load document data for {document_id}")
                return

            logger.info(f"Starting processing pipeline for document {document_id}")
            
            # Stage 1: OCR Extraction
            raw_text = await self._execute_ocr_stage(document_id, file_url)
            
            # Stage 2: AI Analysis  
            insights_result = await self._execute_analysis_stage(document_id, raw_text)
            
            # Stage 3: Save Results
            await self._execute_save_stage(document_id, filename, raw_text, insights_result)
            
            logger.info(f"✅ Document {document_id} processing complete!")

        except Exception as e:
            logger.error(f"Async processing error for document {document_id}: {e}", exc_info=True)
            self._mark_document_error(document_id, str(e))

    async def _execute_ocr_stage(self, document_id: str, file_url: str) -> str:
        """
        Execute OCR extraction stage with progress tracking.
        
        Args:
            document_id: ID of the document being processed
            file_url: URL to the document file
            
        Returns:
            str: Extracted text from the document
            
        Raises:
            ValueError: If OCR extraction yields no text
        """
        logger.info(f"📄 Stage 1/4: Starting OCR extraction for {document_id}")
        self._update_processing_stage(document_id, ProcessingStage.OCR_EXTRACTION)
        
        raw_text = self.ocr_agent.extract_text(file_url)
        if not raw_text or not raw_text.strip():
            raise ValueError("OCR process yielded no text")
            
        return raw_text

    async def _execute_analysis_stage(self, document_id: str, raw_text: str) -> HealthInsights:
        """
        Execute AI analysis stage with progress tracking.
        
        Args:
            document_id: ID of the document being processed
            raw_text: Extracted text content from OCR stage
            
        Returns:
            HealthInsights: Structured health insights from AI analysis
        """
        # --- Stage 2a: Data Extraction ---
        logger.info(f"🧠 Stage 2a/4: Starting Data Extraction for {document_id} ({len(raw_text)} chars)")
        self._update_processing_stage(document_id, ProcessingStage.AI_ANALYSIS, {"raw_text": raw_text, "progress": 30})
        extracted_data = await self.extraction_agent.extract_data(raw_text)
        if not extracted_data.markers:
            logger.warning(f"ExtractionAgent returned no markers for document {document_id}")
            # Optional: you could raise an error here if no markers is a critical failure
            # raise ValueError("Extraction process yielded no health markers")

        # --- Stage 2b: Insight Generation ---
        logger.info(f"🧠 Stage 2b/4: Starting Insight Generation for {document_id}")
        self._update_processing_stage(document_id, ProcessingStage.AI_ANALYSIS, {"progress": 50})
        insights_result = await self.insight_agent.generate_insights(extracted_data)
        
        return insights_result

    async def _execute_save_stage(self, document_id: str, filename: str, raw_text: str, insights_result: HealthInsights):
        """
        Execute save results stage with progress tracking.
        
        Args:
            document_id: ID of the document being processed
            filename: Original filename of the document
            raw_text: Extracted text content from OCR stage
            insights_result: Health insights from AI analysis
        """
        logger.info(f"💾 Stage 3/4: Saving analysis results for {document_id}")
        self._update_processing_stage(document_id, ProcessingStage.SAVING_RESULTS)
        
        # Add brief delay for stage visibility
        await asyncio.sleep(0.5)
        
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
        self._save_document_data(document_id, final_data)

    # === PRIVATE STORAGE METHODS ===
    
    def _upload_to_storage(self, file_content: bytes, storage_path: str) -> str:
        """
        Upload file to Supabase storage and return public URL.
        
        Args:
            file_content: Binary content of the file
            storage_path: Path where the file will be stored
            
        Returns:
            str: Public URL to access the uploaded file
        """
        self.supabase.storage.from_(self.bucket_name).upload(
            path=storage_path,
            file=file_content,
            file_options={"cache-control": "3600", "content-type": "application/pdf"}
        )
        return self.supabase.storage.from_(self.bucket_name).get_public_url(storage_path)

    async def _delete_storage_file(self, storage_path: Optional[str]):
        """
        Delete file from storage if path exists.
        
        Args:
            storage_path: Path to the file in storage
        """
        if storage_path:
            try:
                self.supabase.storage.from_(self.bucket_name).remove([storage_path])
                logger.info(f"Deleted file from storage: {storage_path}")
            except Exception as e:
                logger.warning(f"Failed to delete storage file {storage_path}: {e}")

    async def _delete_storage_file_with_retry(self, storage_path: str):
        """
        Delete file from storage with retry logic for resilience.
        
        Args:
            storage_path: Path to the file in storage
            
        Raises:
            Exception: If all retry attempts fail
        """
        max_retries = 3
        retry_delay = 1.0
        
        for attempt in range(max_retries):
            try:
                self.supabase.storage.from_(self.bucket_name).remove([storage_path])
                logger.info(f"Deleted file from storage: {storage_path}")
                return
            except Exception as e:
                if attempt < max_retries - 1:
                    logger.warning(f"Storage file deletion attempt {attempt + 1} failed for {storage_path}: {e}")
                    logger.info(f"Retrying storage file deletion in {retry_delay} seconds...")
                    await asyncio.sleep(retry_delay)
                    retry_delay *= 2
                else:
                    logger.error(f"All storage file deletion attempts failed for {storage_path}: {e}")
                    raise

    # === PRIVATE DATABASE METHODS ===
    
    def _create_document_record(self, document_id: str, filename: str, storage_path: str, public_url: str):
        """
        Create initial document record in database.
        
        Args:
            document_id: Unique identifier for the document
            filename: Original name of the uploaded file
            storage_path: Path where the file is stored
            public_url: Public URL to access the file
            
        Raises:
            Exception: If database operation fails
        """
        try:
            document_data = {
                "id": document_id,
                "filename": filename,
                "status": "processing",
                "storage_path": storage_path,
                "public_url": public_url,
                "upload_date": datetime.now().isoformat()
            }
            self.supabase.table("documents").insert(document_data).execute()
            logger.info(f"Created initial record for document {document_id}")
        except Exception as e:
            logger.error(f"Error creating document record {document_id}: {e}", exc_info=True)
            raise

    def _update_processing_stage(self, document_id: str, stage: str, extra_data: Optional[Dict] = None):
        """
        Update document processing stage and progress.
        
        Args:
            document_id: ID of the document being processed
            stage: Current processing stage
            extra_data: Additional data to save with the update
        """
        update_data = {
            "status": "processing",
            "processing_stage": stage,
            "progress": STAGE_PROGRESS[stage]
        }
        if extra_data:
            update_data.update(extra_data)
        self._save_document_data(document_id, update_data)

    def _mark_document_error(self, document_id: str, error_message: str):
        """
        Mark document as failed with error message.
        
        Args:
            document_id: ID of the document
            error_message: Description of the error
        """
        if self._load_document_data(document_id):
            self._save_document_data(document_id, {
                "status": "error", 
                "error_message": error_message
            })

    def _save_document_data(self, document_id: str, data: Dict):
        """
        Save/update document data to database with analysis results if complete.
        
        Handles both document metadata updates and complete analysis persistence.
        
        Args:
            document_id: ID of the document
            data: Document data to save
            
        Raises:
            Exception: If database operation fails
        """
        try:
            logger.info(f"Updating document {document_id} with status: {data.get('status')}")

            # Always update main document table
            self._update_document_table(document_id, data)

            # Save analysis results if processing is complete
            if data.get("status") == "complete" and "analysis" in data:
                self._save_analysis_results(document_id, data["analysis"])

        except Exception as e:
            logger.error(f"Error saving document data for {document_id}: {e}", exc_info=True)
            # Fallback: mark as error
            self.supabase.table("documents").update({
                "status": "error", 
                "error_message": str(e)
            }).eq("id", document_id).execute()
            raise

    def _update_document_table(self, document_id: str, data: Dict):
        """
        Update main documents table with processing status and metadata.
        
        Args:
            document_id: ID of the document
            data: Document data to update
        """
        doc_payload = {
            "status": data["status"],
            "error_message": data.get("error_message"),
            "progress": data.get("progress"),
            "processing_stage": data.get("processing_stage")
        }

        # Include raw_text during OCR stage
        if "raw_text" in data:
            doc_payload["raw_text"] = data["raw_text"]

        # Set processed timestamp for completed documents
        if data["status"] == "complete":
            doc_payload["processed_at"] = datetime.now().isoformat()

        self.supabase.table("documents").update(doc_payload).eq("id", document_id).execute()

    def _save_analysis_results(self, document_id: str, analysis_data: Dict):
        """
        Save structured analysis results and health markers to database.
        
        Args:
            document_id: ID of the document
            analysis_data: Structured analysis data to save
        """
        # Get the raw_text from documents table to include it in analysis_results
        doc_result = self.supabase.table("documents").select("raw_text").eq("id", document_id).maybe_single().execute()
        raw_text = doc_result.data.get("raw_text") if doc_result.data else None
        
        # Save analysis result record
        analysis_payload = {
            "document_id": document_id,
            "raw_text": raw_text,
            "structured_data": analysis_data,
            "insights": self._format_insights_as_markdown(HealthInsights(**analysis_data))
        }
        
        analysis_result = self.supabase.table("analysis_results").upsert(
            analysis_payload, on_conflict="document_id"
        ).execute()
        analysis_id = analysis_result.data[0]['id']

        # Save health markers if available
        markers = analysis_data.get("data", {}).get("markers", [])
        if markers:
            self._save_health_markers(analysis_id, markers)

    def _save_health_markers(self, analysis_id: str, markers: List[Dict]):
        """
        Save health markers for an analysis result.
        
        Args:
            analysis_id: ID of the analysis result
            markers: List of health markers to save
        """
        # Clear existing markers to prevent duplicates
        self.supabase.table("health_markers").delete().eq("analysis_id", analysis_id).execute()
        
        # Insert new markers
        markers_payload = [
            {
                "analysis_id": analysis_id,
                "marker_name": marker.get("marker"),
                "value": marker.get("value"),
                "unit": marker.get("unit"),
                "reference_range": marker.get("reference_range"),
            } for marker in markers
        ]
        self.supabase.table("health_markers").insert(markers_payload).execute()
        logger.info(f"Saved {len(markers_payload)} health markers for analysis {analysis_id}")

    async def _delete_analysis_data(self, document_id: str):
        """
        Delete analysis results and associated health markers.
        
        Args:
            document_id: ID of the document
        """
        analysis_result = self.supabase.table("analysis_results").select("id").eq(
            "document_id", document_id
        ).maybe_single().execute()
        
        if analysis_result.data:
            analysis_id = analysis_result.data["id"]
            
            # Delete markers first (foreign key constraint)
            self.supabase.table("health_markers").delete().eq("analysis_id", analysis_id).execute()
            logger.info(f"Deleted health markers for analysis {analysis_id}")
            
            # Delete analysis result
            self.supabase.table("analysis_results").delete().eq("id", analysis_id).execute()
            logger.info(f"Deleted analysis result {analysis_id}")

    def _load_document_data(self, document_id: str) -> Optional[Dict]:
        """
        Load document data from database.
        
        Args:
            document_id: ID of the document to load
            
        Returns:
            Optional[Dict]: Document data or None if not found
        """
        try:
            result = self.supabase.table("documents").select("*").eq("id", document_id).maybe_single().execute()
            return result.data
        except Exception as e:
            logger.error(f"Error loading document data for {document_id}: {e}", exc_info=True)
            return None

    def _delete_document_record(self, document_id: str):
        """
        Delete main document record from database.
        
        Args:
            document_id: ID of the document to delete
        """
        self.supabase.table("documents").delete().eq("id", document_id).execute()
        logger.info(f"Deleted document record {document_id}")

    # === PRIVATE FORMATTING METHODS ===
    
    def _format_insights_as_markdown(self, insights: HealthInsights) -> str:
        """
        Convert structured insights to markdown format for frontend display.
        
        Args:
            insights: Structured health insights
            
        Returns:
            str: Formatted markdown string
        """
        md = f"# Analysis Report\n\n## Summary\n{insights.summary}\n\n"
        md += "## Key Findings\n" + "".join([f"- {finding}\n" for finding in insights.key_findings])
        md += "\n## Recommendations\n" + "".join([f"- {rec}\n" for rec in insights.recommendations])
        md += f"\n---\n\n**Disclaimer:** {insights.disclaimer}"
        return md

    def _format_iso_date(self, date_val: Optional[datetime]) -> Optional[str]:
        """Safely format a datetime object to ISO 8601 string."""
        if isinstance(date_val, datetime):
            return date_val.isoformat()
        return date_val

    def _format_document_for_frontend(self, doc: Dict) -> Dict:
        """
        Format document data with consistent field names for frontend.
        
        Args:
            doc: Document data from database
            
        Returns:
            Dict: Formatted document data for frontend
        """
        # Handle date field renaming and formatting
        upload_date = doc.get("upload_date")
        if isinstance(upload_date, datetime):
            upload_date = upload_date.isoformat()
            
        processed_at = doc.get("processed_at")
        if isinstance(processed_at, datetime):
            processed_at = processed_at.isoformat()

        return {
            **doc,
            "uploaded_at": self._format_iso_date(doc.get("upload_date")),
            "processed_at": self._format_iso_date(doc.get("processed_at")),
        }