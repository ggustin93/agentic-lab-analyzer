# backend/services/document_processor.py

import asyncio
import uuid
import os
import json
from datetime import datetime
from typing import Dict, List, Optional
import logging

from supabase import create_client, Client

from config.settings import settings
from models.health_models import HealthInsights
from .base import OCRExtractorAgent
from .mistral_ocr_service import MistralOCRService
from .data_extractor_agent import LabDataExtractorAgent
from .clinical_insight_agent import ClinicalInsightAgent


logger = logging.getLogger(__name__)

class DocumentProcessor:
    """
    Acts as the central orchestrator for the document analysis pipeline.
    This service manages the flow of a document through various specialized agents,
    from initial OCR to final clinical insight generation, while also handling
    database state and real-time progress updates.
    """
    
    def __init__(self):
        """
        Initializes the processor and its dependent agents.
        In a larger system, these dependencies would be injected for better
        testability, but for this project's scope, direct instantiation is sufficient.
        """
        # --- Agent Initialization ---
        self.ocr_agent: OCRExtractorAgent = MistralOCRService()
        self.extractor_agent: LabDataExtractorAgent = LabDataExtractorAgent()
        self.insight_agent: ClinicalInsightAgent = ClinicalInsightAgent()
        
        # --- Database & Storage Client ---
        self.supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        self.bucket_name: str = settings.SUPABASE_BUCKET_NAME
    
    async def process_document(self, file_content: bytes, filename: str) -> str:
        """
        Handles the initial upload of a document and initiates the asynchronous
        processing pipeline in the background.

        Args:
            file_content: The binary content of the file.
            filename: The original name of the file.

        Returns:
            The unique ID of the document record created.
            
        Raises:
            Exception: If the initial upload or database record creation fails.
        """
        document_id = str(uuid.uuid4())
        file_extension = os.path.splitext(filename)[1]
        storage_path = f"{document_id}{file_extension}"

        try:
            # Step 1: Upload the raw file to Supabase Storage for persistence.
            # TODO: Infer content-type dynamically instead of hardcoding.
            self.supabase.storage.from_(self.bucket_name).upload(
                path=storage_path,
                file=file_content,
                file_options={"content-type": "application/pdf"}
            )
            public_url = self.supabase.storage.from_(self.bucket_name).get_public_url(storage_path)

            # Step 2: Create the initial document record in the database.
            self._create_document_record(document_id, filename, storage_path, public_url)

            # Step 3: Schedule the main processing pipeline to run in the background.
            # This allows us to return an immediate response to the client.
            asyncio.create_task(self._process_document_async(document_id, public_url, file_extension))
            
            return document_id
            
        except Exception as e:
            logger.error(f"Initial document processing error for {filename}: {e}", exc_info=True)
            # Attempt to mark the record as failed if it was created.
            try:
                self._update_progress(document_id, 100, "error", error_message=str(e))
            except Exception as db_e:
                logger.error(f"Could not update document {document_id} to error state: {db_e}")
            raise

    def _create_document_record(self, document_id: str, filename: str, storage_path: str, public_url: str):
        """Creates the initial document metadata record in the 'documents' table."""
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

    async def _process_document_async(self, document_id: str, file_url: str, file_type: str):
        """
        Executes the main multi-agent processing pipeline asynchronously.

        This method orchestrates the flow of data through the following stages:
        1. OCR Extraction: Converts the document to raw text.
        2. Data Extraction & Analysis: Extracts structured data and analyzes it.
        3. Clinical Insight Generation: Generates human-readable insights.
        4. Persistence: Saves the final results to the database.
        """
        try:
            # --- Agent 1: OCR Extraction ---
            self._update_progress(document_id, 10, "ocr_extraction")
            raw_text = await self.ocr_agent.extract_text(file_url, file_type)
            if not raw_text or not raw_text.strip():
                raise ValueError("OCR process yielded no text.")
            
            # Persist raw text as soon as it's available for debugging and transparency.
            self.supabase.table("documents").update({"raw_text": raw_text}).eq("id", document_id).execute()

            # --- Agent 2: Extract structured data & analyze ranges ---
            self._update_progress(document_id, 40, "ai_analysis_extraction")
            async with self.extractor_agent as extractor_agent:
                analyzed_data = await extractor_agent.extract_and_analyze(raw_text)
            
            # --- Agent 3: Clinical Insight Generation ---
            self._update_progress(document_id, 70, "ai_analysis_insights")
            async with self.insight_agent as insight_agent:
                insight_dict = await insight_agent.generate_insights(analyzed_data)

            # --- Final Response Construction & Persistence ---
            self._update_progress(document_id, 90, "saving_results")
            
            final_data = HealthInsights(data=analyzed_data, **insight_dict)

            analysis_payload = {
                "document_id": document_id,
                "structured_data": final_data.model_dump(mode='json'),
                "insights": self._format_insights_as_markdown(final_data)
            }
            self.supabase.table("analysis_results").upsert(analysis_payload, on_conflict="document_id").execute()

            # Mark the process as complete.
            self._update_progress(document_id, 100, "complete")
            logger.info(f"Successfully processed and saved document {document_id}")

        except Exception as e:
            logger.error(f"Async processing error for document {document_id}: {e}", exc_info=True)
            self._update_progress(document_id, 100, "error", error_message=str(e))

    def _update_progress(self, document_id: str, progress: int, stage: str, error_message: Optional[str] = None):
        """
        Updates the document's progress and status in the database.
        This is a central helper to ensure consistent state management.
        """
        status = "processing"
        if error_message:
            status = "error"
        elif progress == 100:
            status = "complete"

        payload = {
            "progress": progress,
            "processing_stage": stage,
            "status": status,
        }
        if error_message:
            payload["error_message"] = error_message
        if status == "complete":
            payload["processed_at"] = datetime.now().isoformat()
        
        logger.info(f"Updating document {document_id}: {payload}")
        self.supabase.table("documents").update(payload).eq("id", document_id).execute()
        
    def _format_insights_as_markdown(self, insights: HealthInsights) -> str:
        """Converts the final HealthInsights object into a formatted markdown string."""
        md_parts = [
            f"## Health Analysis Summary\n\n{insights.summary}\n",
            "### Key Findings\n"
        ]
        md_parts.extend(f"- {finding}\n" for finding in insights.key_findings)
        md_parts.append("\n### Recommendations\n")
        md_parts.extend(f"- {rec}\n" for rec in insights.recommendations)
        md_parts.append(f"\n---\n\n*{insights.disclaimer}*")
        return "".join(md_parts)

    def get_analysis(self, document_id: str) -> Optional[Dict]:
        """
        Retrieves the complete analysis for a given document ID, composing data
        from multiple tables into a single, frontend-ready object.
        """
        logger.info(f"Retrieving analysis for document {document_id}")
        doc_response = self.supabase.table("documents").select("*").eq("id", document_id).maybe_single().execute()
        
        if not doc_response.data:
            return None
        
        doc = doc_response.data
        
        # Base structure from the main document record.
        analysis_payload = {
            "document_id": doc.get("id"),
            "status": doc.get("status"),
            "filename": doc.get("filename"),
            "uploaded_at": doc.get("upload_date"),
            "raw_text": doc.get("raw_text"),
            "error_message": doc.get("error_message"),
            "processed_at": doc.get("processed_at"),
            "progress": doc.get("progress"),
            "processing_stage": doc.get("processing_stage"),
            "ai_insights": None,
            "extracted_data": []
        }

        # If processing is complete, fetch and integrate the analysis results.
        if analysis_payload["status"] == "complete":
            analysis_result_response = self.supabase.table("analysis_results").select("structured_data, insights").eq("document_id", document_id).maybe_single().execute()
            if analysis_result_response.data:
                ar = analysis_result_response.data
                analysis_payload["ai_insights"] = ar.get("insights")
                
                # The structured_data field contains the full HealthInsights object as JSON.
                # We parse it to populate the extracted_data.
                structured_data = ar.get("structured_data", {})
                if structured_data and 'data' in structured_data and 'markers' in structured_data['data']:
                    analysis_payload["extracted_data"] = structured_data['data']['markers']

        return analysis_payload
        
    async def delete_document(self, document_id: str) -> bool:
        """
        Deletes a document from storage and its associated records from the database.
        The database schema is configured with `ON DELETE CASCADE` to automatically
        remove dependent records in `analysis_results`.
        """
        logger.info(f"Attempting to delete document {document_id}")
        
        # Retrieve the storage path before deleting the database record.
        doc_res = self.supabase.table("documents").select("storage_path").eq("id", document_id).maybe_single().execute()
        
        # Delete the primary document record. The CASCADE constraint handles the rest.
        delete_res = self.supabase.table("documents").delete().eq("id", document_id).execute()
        
        if not delete_res.data:
            logger.warning(f"Document {document_id} not found in DB for deletion, but proceeding to check storage.")
            # Even if DB record is gone, try to clean up storage if we have the path.
            if doc_res.data and doc_res.data.get("storage_path"):
                 pass # fall through to storage deletion
            else:
                return False

        # If the database record was found and deleted, proceed to delete the file from storage.
        if doc_res.data and (storage_path := doc_res.data.get("storage_path")):
            try:
                self.supabase.storage.from_(self.bucket_name).remove([storage_path])
                logger.info(f"Successfully deleted file from storage: {storage_path}")
            except Exception as e:
                # Log the error but return True, as the primary records are gone.
                logger.error(f"DB records for {document_id} were deleted, but storage cleanup failed: {e}")
        
        logger.info(f"Successfully deleted document {document_id} and associated data.")
        return True
    
    async def list_documents(self) -> List[Dict]:
        """Lists all documents with key metadata, formatted for the frontend."""
        result = self.supabase.table("documents").select(
            "id, filename, upload_date, status, processed_at, public_url, progress, processing_stage"
        ).order("upload_date", desc=True).execute()
        
        documents = result.data or []
        # Frontend expects 'uploaded_at', so we rename the field for consistency.
        for doc in documents:
            doc['uploaded_at'] = doc.pop('upload_date', None)
        return documents