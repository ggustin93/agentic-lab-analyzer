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
from .chutes_ai_agent import ChutesAILabAgent

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
        self.ocr_agent: OCRExtractorAgent = MistralOCRService()
        self.insight_agent: LabInsightAgent = ChutesAILabAgent()
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
        Delete a document and all associated data from storage and database.
        
        Args:
            document_id: ID of document to delete
            
        Returns:
            bool: True if deletion successful, False if document not found
        """
        try:
            document_data = self._load_document_data(document_id)
            if not document_data:
                logger.warning(f"Document {document_id} not found for deletion")
                return False

            # Delete in correct order to respect foreign key constraints
            await self._delete_analysis_data(document_id)
            await self._delete_storage_file(document_data.get("storage_path"))
            self._delete_document_record(document_id)

            logger.info(f"Successfully deleted document {document_id}")
            return True

        except Exception as e:
            logger.error(f"Error deleting document {document_id}: {e}", exc_info=True)
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
        Get comprehensive analysis data for a document.
        
        Args:
            document_id: ID of document to retrieve
            
        Returns:
            Optional[Dict]: Formatted document data with analysis results, or None if not found
        """
        try:
            document_data = self._load_document_data(document_id)
            if not document_data:
                return None

            # Build base document structure
            doc = self._build_base_document_response(document_data)
            
            # Attach analysis results if processing is complete
            if doc["status"] == "complete":
                self._attach_analysis_results(doc, document_id)
            
            return doc
            
        except Exception as e:
            logger.error(f"Error retrieving analysis for {document_id}: {e}", exc_info=True)
            return None
    
    # === PRIVATE PROCESSING METHODS ===
    
    async def _process_document_async(self, document_id: str, file_url: str, filename: str):
        """
        Execute the complete async processing pipeline with stage tracking.
        
        Pipeline: OCR Extraction → AI Analysis → Save Results → Complete
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
        """Execute OCR extraction stage with progress tracking."""
        logger.info(f"📄 Stage 1/4: Starting OCR extraction for {document_id}")
        self._update_processing_stage(document_id, ProcessingStage.OCR_EXTRACTION)
        
        raw_text = self.ocr_agent.extract_text(file_url)
        if not raw_text or not raw_text.strip():
            raise ValueError("OCR process yielded no text")
            
        return raw_text

    async def _execute_analysis_stage(self, document_id: str, raw_text: str) -> HealthInsights:
        """Execute AI analysis stage with progress tracking."""
        logger.info(f"🧠 Stage 2/4: Starting AI analysis for {document_id} ({len(raw_text)} chars)")
        self._update_processing_stage(document_id, ProcessingStage.AI_ANALYSIS, {"raw_text": raw_text})
        
        return await self.insight_agent.analyze_text(raw_text)

    async def _execute_save_stage(self, document_id: str, filename: str, raw_text: str, insights_result: HealthInsights):
        """Execute save results stage with progress tracking."""
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
        """Upload file to Supabase storage and return public URL."""
        self.supabase.storage.from_(self.bucket_name).upload(
            path=storage_path,
            file=file_content,
            file_options={"cache-control": "3600", "content-type": "application/pdf"}
        )
        return self.supabase.storage.from_(self.bucket_name).get_public_url(storage_path)

    async def _delete_storage_file(self, storage_path: Optional[str]):
        """Delete file from storage if path exists."""
        if storage_path:
            try:
                self.supabase.storage.from_(self.bucket_name).remove([storage_path])
                logger.info(f"Deleted file from storage: {storage_path}")
            except Exception as e:
                logger.warning(f"Failed to delete storage file {storage_path}: {e}")

    # === PRIVATE DATABASE METHODS ===
    
    def _create_document_record(self, document_id: str, filename: str, storage_path: str, public_url: str):
        """Create initial document record in database."""
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
        """Update document processing stage and progress."""
        update_data = {
            "status": "processing",
            "processing_stage": stage,
            "progress": STAGE_PROGRESS[stage]
        }
        if extra_data:
            update_data.update(extra_data)
        self._save_document_data(document_id, update_data)

    def _mark_document_error(self, document_id: str, error_message: str):
        """Mark document as failed with error message."""
        if self._load_document_data(document_id):
            self._save_document_data(document_id, {
                "status": "error", 
                "error_message": error_message
            })

    def _save_document_data(self, document_id: str, data: Dict):
        """
        Save/update document data to database with analysis results if complete.
        
        Handles both document metadata updates and complete analysis persistence.
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
        """Update main documents table with processing status and metadata."""
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
        """Save structured analysis results and health markers to database."""
        # Save analysis result record
        analysis_payload = {
            "document_id": document_id,
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
        """Save health markers for an analysis result."""
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

    def _load_document_data(self, document_id: str) -> Optional[Dict]:
        """Load complete document data from database including analysis if available."""
        try:
            result = self.supabase.table("documents").select("*").eq("id", document_id).maybe_single().execute()
            if not result.data:
                return None
            
            doc = result.data

            # Attach analysis data if document is complete
            if doc["status"] == "complete":
                doc = self._attach_analysis_to_document(doc)

            return doc

        except Exception as e:
            logger.error(f"Error loading document data for {document_id}: {e}", exc_info=True)
            return None

    def _attach_analysis_to_document(self, doc: Dict) -> Dict:
        """Attach analysis results and markers to document data."""
        analysis_result = self.supabase.table("analysis_results").select("*").eq(
            "document_id", doc["id"]
        ).maybe_single().execute()
        
        if analysis_result.data:
            doc["analysis"] = analysis_result.data
            
            # Attach health markers
            markers_result = self.supabase.table("health_markers").select("*").eq(
                "analysis_id", analysis_result.data['id']
            ).execute()
            if markers_result.data:
                doc["analysis"]["markers"] = markers_result.data

        return doc

    async def _delete_analysis_data(self, document_id: str):
        """Delete analysis results and associated health markers."""
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

    def _delete_document_record(self, document_id: str):
        """Delete main document record from database."""
        self.supabase.table("documents").delete().eq("id", document_id).execute()
        logger.info(f"Deleted document record {document_id}")

    # === PRIVATE FORMATTING METHODS ===
    
    def _format_insights_as_markdown(self, insights: HealthInsights) -> str:
        """Convert structured insights to markdown format for frontend display."""
        md = f"# Analysis Report\n\n## Summary\n{insights.summary}\n\n"
        md += "## Key Findings\n" + "".join([f"- {finding}\n" for finding in insights.key_findings])
        md += "\n## Recommendations\n" + "".join([f"- {rec}\n" for rec in insights.recommendations])
        md += f"\n---\n\n**Disclaimer:** {insights.disclaimer}"
        return md

    def _format_document_for_frontend(self, doc: Dict) -> Dict:
        """Format document data with consistent field names for frontend."""
        # Handle date field renaming and formatting
        upload_date = doc.get("upload_date")
        if isinstance(upload_date, datetime):
            upload_date = upload_date.isoformat()
            
        processed_at = doc.get("processed_at")
        if isinstance(processed_at, datetime):
            processed_at = processed_at.isoformat()

        return {
            **doc,
            "uploaded_at": upload_date,  # Frontend expects 'uploaded_at'
            "processed_at": processed_at
        }

    def _build_base_document_response(self, document_data: Dict) -> Dict:
        """Build base document response structure for get_analysis."""
        upload_date = document_data.get("upload_date")
        if isinstance(upload_date, datetime):
            upload_date = upload_date.isoformat()
            
        processed_at = document_data.get("processed_at")
        if isinstance(processed_at, datetime):
            processed_at = processed_at.isoformat()

        return {
            "document_id": document_data["id"],
            "status": document_data.get("status"),
            "filename": document_data.get("filename"),
            "uploaded_at": upload_date,
            "raw_text": document_data.get("raw_text"),
            "error_message": document_data.get("error_message"),
            "processed_at": processed_at,
            "progress": document_data.get("progress"),
            "processing_stage": document_data.get("processing_stage"),
            "ai_insights": None,
            "extracted_data": []
        }

    def _attach_analysis_results(self, doc: Dict, document_id: str):
        """Attach analysis results and markers to document response."""
        analysis_result = self.supabase.table("analysis_results").select("*").eq(
            "document_id", document_id
        ).maybe_single().execute()
        
        if analysis_result.data:
            analysis_data = analysis_result.data
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