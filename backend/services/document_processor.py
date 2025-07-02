import asyncio
import uuid
import os
import json
from datetime import datetime
from typing import Dict, List, Optional
import logging

from supabase import create_client, Client

from config.settings import settings
from models.document_models import Document, AnalysisResult, HealthMarkerDB
from models.health_models import HealthInsights
from agents.base import OCRExtractorAgent, LabInsightAgent
from .mistral_ocr_service import MistralOCRService
from .chutes_ai_agent import ChutesAILabAgent

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Main service for processing health documents."""
    
    def __init__(self):
        self.ocr_agent: OCRExtractorAgent = MistralOCRService()
        self.insight_agent: LabInsightAgent = ChutesAILabAgent()
        self.supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
        self.bucket_name = settings.SUPABASE_BUCKET_NAME
    
    async def process_document(self, file_content: bytes, filename: str) -> str:
        """Process a document and return document ID"""
        document_id = str(uuid.uuid4())
        file_extension = os.path.splitext(filename)[1]
        storage_path = f"{document_id}{file_extension}"

        try:
            # Upload file to Supabase Storage
            self.supabase.storage.from_(self.bucket_name).upload(
                path=storage_path,
                file=file_content,
                file_options={"cache-control": "3600", "content-type": "application/pdf"}
            )
            public_url = self.supabase.storage.from_(self.bucket_name).get_public_url(storage_path)

            # Create initial document record in Supabase
            self._create_document_record(document_id, filename, storage_path, public_url)

            # Start background processing
            asyncio.create_task(self._process_document_async(document_id, public_url, filename))
            
            return document_id
            
        except Exception as e:
            logger.error(f"Document processing error: {e}", exc_info=True)
            # If the record was created, update its status to error
            if self._load_document_data(document_id):
                 self._save_document_data(document_id, {"status": "error", "error_message": str(e)})
            raise

    def _create_document_record(self, document_id: str, filename: str, storage_path: str, public_url: str):
        """Create the initial document record in the database."""
        try:
            document_data = {
                "id": document_id,
                "filename": filename,
                "status": "processing",
                "storage_path": storage_path,
                "public_url": public_url,
                "upload_date": datetime.now().isoformat()  # Explicitly set upload_date as ISO string
            }
            self.supabase.table("documents").insert(document_data).execute()
            logger.info(f"Successfully created initial record for document {document_id}")
        except Exception as e:
            logger.error(f"Error creating initial record for document {document_id}: {e}", exc_info=True)
            raise

    async def _process_document_async(self, document_id: str, file_url: str, filename: str):
        """Async processing of document with PydanticAI"""
        try:
            document_data = self._load_document_data(document_id)
            if not document_data:
                logger.error(f"Could not load document data for {document_id} to start async processing.")
                return

            logger.info(f"Starting PydanticAI processing for document {document_id}")
            
            # Update status with progress information - OCR starting
            self._save_document_data(document_id, {
                "status": "processing",
                "processing_stage": "ocr_extraction",
                "progress": 10
            })
            
            # Use the ocr_agent to extract text from the file
            raw_text = self.ocr_agent.extract_text(file_url)

            if not raw_text or not raw_text.strip():
                raise ValueError("OCR process yielded no text")
            
            # Update status with progress information - OCR complete, starting analysis
            self._save_document_data(document_id, {
                "status": "processing",
                "processing_stage": "ai_analysis",
                "progress": 50,
                "raw_text": raw_text
            })
            
            # Get health insights using the extracted text
            insights_result = await self.insight_agent.analyze_text(raw_text)

            # Update status with progress information - analysis complete, saving results
            self._save_document_data(document_id, {
                "status": "processing",
                "processing_stage": "saving_results",
                "progress": 90
            })

            # Final data structure for saving
            final_data = {
                "id": document_id,
                "filename": filename,
                "status": "complete",
                "raw_text": raw_text,
                "analysis": insights_result.model_dump(mode='json'),
                "progress": 100,
                "processing_stage": "complete"
            }
            self._save_document_data(document_id, final_data)
            logger.info(f"Successfully processed and saved document {document_id}")

        except Exception as e:
            logger.error(f"Async processing error for document {document_id}: {e}", exc_info=True)
            error_data = {
                "status": "error",
                "error_message": str(e)
            }
            self._save_document_data(document_id, error_data)

    def _format_insights_as_markdown(self, insights: HealthInsights) -> str:
        # Helper function to convert the structured insights object to a single markdown string for the frontend
        md = f"# Analysis Report\n\n## Summary\n{insights.summary}\n\n"
        md += "## Key Findings\n" + "".join([f"- {finding}\n" for finding in insights.key_findings])
        md += "\n## Recommendations\n" + "".join([f"- {rec}\n" for rec in insights.recommendations])
        md += f"\n---\n\n**Disclaimer:** {insights.disclaimer}"
        return md

    def get_analysis(self, document_id: str) -> Optional[Dict]:
        """Get analysis data for a document by ID"""
        try:
            document_data = self._load_document_data(document_id)
            if not document_data:
                return None

            # Format dates as ISO strings
            upload_date = document_data.get("upload_date")
            if isinstance(upload_date, datetime):
                upload_date = upload_date.isoformat()
                
            processed_at = document_data.get("processed_at")
            if isinstance(processed_at, datetime):
                processed_at = processed_at.isoformat()

            # Base document info that is always present
            doc = {
                "document_id": document_id,
                "status": document_data.get("status"),
                "filename": document_data.get("filename"),
                "uploaded_at": upload_date,  # Changed from upload_date to uploaded_at to match frontend
                "raw_text": document_data.get("raw_text"),
                "error_message": document_data.get("error_message"),
                "processed_at": processed_at,
                "progress": document_data.get("progress"),  # Include progress for SSE updates
                "processing_stage": document_data.get("processing_stage"),  # Include processing stage for SSE updates
                "ai_insights": None,
                "extracted_data": []
            }

            # Fetch and attach analysis results if the document is complete
            if doc["status"] == "complete":
                analysis_result_response = self.supabase.table("analysis_results").select("*").eq("document_id", document_id).maybe_single().execute()
                
                if analysis_result_response.data:
                    analysis_data = analysis_result_response.data
                    doc["ai_insights"] = analysis_data.get("insights")
                    
                    # Fetch markers from the correct table
                    markers_result = self.supabase.table("health_markers").select("marker_name, value, unit, reference_range").eq("analysis_id", analysis_data['id']).execute()
                    if markers_result.data:
                        # Map database column names to what frontend expects
                        doc["extracted_data"] = [{
                            "marker": item["marker_name"],
                            "value": item["value"],
                            "unit": item["unit"],
                            "reference_range": item["reference_range"]
                        } for item in markers_result.data]
                        logger.info(f"Found {len(doc['extracted_data'])} markers for document {document_id}")
            
            return doc
            
        except Exception as e:
            logger.error(f"Error retrieving analysis for {document_id}: {e}", exc_info=True)
            return None
    
    async def delete_document(self, document_id: str) -> bool:
        """Delete a document and all its associated data from Supabase"""
        try:
            # 1. Load document data first to get storage path
            document_data = self._load_document_data(document_id)
            if not document_data:
                logger.warning(f"Document {document_id} not found for deletion")
                return False

            storage_path = document_data.get("storage_path")

            # 2. Get analysis_result ID to delete related health markers  
            analysis_result = self.supabase.table("analysis_results").select("id").eq("document_id", document_id).maybe_single().execute()
            if analysis_result.data:
                analysis_id = analysis_result.data["id"]
                
                # Delete health markers first (foreign key constraint)
                self.supabase.table("health_markers").delete().eq("analysis_id", analysis_id).execute()
                logger.info(f"Deleted health markers for analysis {analysis_id}")
                
                # Delete analysis result
                self.supabase.table("analysis_results").delete().eq("id", analysis_id).execute()
                logger.info(f"Deleted analysis result {analysis_id}")

            # 3. Delete file from storage
            if storage_path:
                try:
                    self.supabase.storage.from_(self.bucket_name).remove([storage_path])
                    logger.info(f"Deleted file from storage: {storage_path}")
                except Exception as e:
                    logger.warning(f"Failed to delete file from storage {storage_path}: {e}")
                    # Continue with database deletion even if storage deletion fails

            # 4. Delete document record (should be last due to foreign key constraints)
            self.supabase.table("documents").delete().eq("id", document_id).execute()
            logger.info(f"Deleted document record {document_id}")

            return True

        except Exception as e:
            logger.error(f"Error deleting document {document_id}: {e}", exc_info=True)
            return False
    
    async def list_documents(self) -> List[Dict]:
        """List all documents from Supabase"""
        try:
            result = self.supabase.table("documents").select("id, filename, upload_date, status, processed_at, public_url").order("upload_date", desc=True).execute()
            documents = result.data if result.data else []
            
            # Ensure dates are properly formatted as ISO strings for frontend
            for doc in documents:
                if 'upload_date' in doc and doc['upload_date']:
                    # Convert to ISO format string if it's not already
                    if isinstance(doc['upload_date'], datetime):
                        # Rename the field to match what frontend expects
                        doc['uploaded_at'] = doc['upload_date'].isoformat()
                        del doc['upload_date']  # Remove the old field
                    else:
                        doc['uploaded_at'] = doc['upload_date']
                        del doc['upload_date']
                if 'processed_at' in doc and doc['processed_at']:
                    if isinstance(doc['processed_at'], datetime):
                        doc['processed_at'] = doc['processed_at'].isoformat()
                        
            return documents
        except Exception as e:
            logger.error(f"Error listing documents from Supabase: {e}")
            return []
    
    def _save_document_data(self, document_id: str, data: Dict):
        """Save/Update document analysis data to Supabase"""
        try:
            logger.info(f"--- SAVING/UPDATING DATA FOR {document_id} ---")
            logger.info(f"DATA RECEIVED: {data}")

            # 1. Always update the main document table
            doc_payload = {
                "status": data["status"],
                "error_message": data.get("error_message")
            }

            if data["status"] == "complete":
                doc_payload["raw_text"] = data.get("raw_text")
                doc_payload["processed_at"] = datetime.now().isoformat()

            logger.info(f"UPDATING 'documents' with payload: {doc_payload}")
            self.supabase.table("documents").update(doc_payload).eq("id", document_id).execute()

            # 2. If processing is complete, save the analysis results
            if data["status"] == "complete" and "analysis" in data:
                logger.info("Status is 'complete', processing analysis results.")
                analysis_payload = {
                    "document_id": document_id,
                    "structured_data": data["analysis"],
                    "insights": self._format_insights_as_markdown(HealthInsights(**data["analysis"]))
                }
                
                # Upsert analysis results
                logger.info(f"UPSERTING 'analysis_results' with payload: {analysis_payload}")
                analysis_result = self.supabase.table("analysis_results").upsert(analysis_payload, on_conflict="document_id").execute()
                logger.info(f"UPSERT result: {analysis_result.data}")
                analysis_id = analysis_result.data[0]['id']

                # 3. Save health markers
                if "data" in data["analysis"] and "markers" in data["analysis"]["data"] and data["analysis"]["data"]["markers"]:
                    logger.info("Processing health markers.")
                    markers_payload = [
                        {
                            "analysis_id": analysis_id,
                            "marker_name": marker.get("marker"),
                            "value": marker.get("value"),
                            "unit": marker.get("unit"),
                            "reference_range": marker.get("reference_range"),
                        } for marker in data["analysis"]["data"]["markers"]
                    ]
                    # Clear old markers before inserting new ones to prevent duplicates
                    logger.info(f"DELETING old markers for analysis_id: {analysis_id}")
                    self.supabase.table("health_markers").delete().eq("analysis_id", analysis_id).execute()
                    logger.info(f"INSERTING new markers: {markers_payload}")
                    self.supabase.table("health_markers").insert(markers_payload).execute()
                else:
                    logger.info("No markers found in analysis data.")
            else:
                logger.info("Status is not 'complete' or no analysis data, skipping analysis save.")

        except Exception as e:
            logger.error(f"Error saving document data for {document_id} to Supabase: {e}", exc_info=True)
            # Try to set the status to error one last time
            self.supabase.table("documents").update({"status": "error", "error_message": str(e)}).eq("id", document_id).execute()
            raise

    def _load_document_data(self, document_id: str) -> Optional[Dict]:
        """Load document data from Supabase"""
        try:
            # Fetch the document from Supabase
            result = self.supabase.table("documents").select("*").eq("id", document_id).maybe_single().execute()
            if not result.data:
                return None
            
            doc = result.data

            # Fetch analysis results and markers if document processing is complete
            if doc["status"] == "complete":
                analysis_result = self.supabase.table("analysis_results").select("*").eq("document_id", document_id).maybe_single().execute()
                if analysis_result.data:
                    doc["analysis"] = analysis_result.data
                    # The markers are nested, let's format them as expected by the frontend
                    doc["extracted_data"] = analysis_result.data.get("health_markers", [])

                    markers_result = self.supabase.table("health_markers").select("*").eq("analysis_id", analysis_result.data['id']).execute()
                    if markers_result.data:
                        doc["analysis"]["markers"] = markers_result.data

            return doc

        except Exception as e:
            logger.error(f"Error loading document data for {document_id} from Supabase: {e}", exc_info=True)
            return None