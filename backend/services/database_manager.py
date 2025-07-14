"""
Database Manager Module

Handles all database operations for document management including CRUD operations,
analysis results, and health markers persistence.
"""

import logging
from datetime import datetime
from typing import Dict, List, Optional
from supabase import Client

from models.health_models import HealthInsights

logger = logging.getLogger(__name__)


class DatabaseManager:
    """
    Manages all database operations for document processing workflow.
    
    Provides clean interface for document lifecycle management, analysis storage,
    and health marker persistence with proper error handling.
    """
    
    def __init__(self, supabase_client: Client):
        """
        Initialize database manager with Supabase client.
        
        Args:
            supabase_client: Configured Supabase client instance
        """
        self.supabase = supabase_client
    
    def create_document_record(self, document_id: str, filename: str, storage_path: str, public_url: str) -> None:
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
    
    def update_processing_stage(self, document_id: str, stage: str, extra_data: Optional[Dict] = None) -> None:
        """
        Update document processing stage and progress.
        
        Args:
            document_id: ID of the document being processed
            stage: Current processing stage
            extra_data: Additional data to save with the update
        """
        try:
            # Determine progress based on stage
            stage_progress = {
                "ocr_extraction": 10,
                "ai_analysis": 50,
                "saving_results": 90,
                "complete": 100
            }
            
            update_data = {
                "processing_stage": stage,
                "progress": stage_progress.get(stage, 0)
            }
            
            # Add extra data if provided
            if extra_data:
                update_data.update(extra_data)
            
            self.supabase.table("documents").update(update_data).eq("id", document_id).execute()
            logger.info(f"Updated processing stage for {document_id}: {stage}")
        except Exception as e:
            logger.error(f"Error updating processing stage for {document_id}: {e}", exc_info=True)
            raise
    
    def mark_document_error(self, document_id: str, error_message: str) -> None:
        """
        Mark document as failed with error message.
        
        Args:
            document_id: ID of the document that failed
            error_message: Error description
        """
        try:
            self.supabase.table("documents").update({
                "status": "error", 
                "error_message": str(error_message)
            }).eq("id", document_id).execute()
            logger.info(f"Marked document {document_id} as error: {error_message}")
        except Exception as e:
            logger.error(f"Error marking document {document_id} as failed: {e}", exc_info=True)
            raise
    
    def update_document_raw_text(self, document_id: str, raw_text: str) -> None:
        """
        Update the raw_text field for a document.
        
        Args:
            document_id: ID of the document to update
            raw_text: The extracted raw text to save
        """
        try:
            self.supabase.table("documents").update({"raw_text": raw_text}).eq("id", document_id).execute()
            logger.info(f"Updated raw_text for document {document_id}")
        except Exception as e:
            logger.error(f"Error updating raw_text for {document_id}: {e}", exc_info=True)
            # We don't re-raise here as this is not a critical failure
            pass

    def update_document_table(self, document_id: str, data: Dict) -> None:
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

        # Set processed timestamp for completed documents
        if data["status"] == "complete":
            doc_payload["processed_at"] = datetime.now().isoformat()

        self.supabase.table("documents").update(doc_payload).eq("id", document_id).execute()
        logger.info(f"Updated document table for {document_id}")
    
    def save_analysis_results(self, document_id: str, analysis_data: Dict) -> None:
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
    
    def _save_health_markers(self, analysis_id: str, markers: List[Dict]) -> None:
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
    
    async def delete_analysis_data(self, document_id: str) -> None:
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
    
    def load_document_data(self, document_id: str) -> Optional[Dict]:
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
    
    def delete_document_record(self, document_id: str) -> None:
        """
        Delete main document record from database.
        
        Args:
            document_id: ID of the document to delete
        """
        self.supabase.table("documents").delete().eq("id", document_id).execute()
        logger.info(f"Deleted document record {document_id}")
    
    async def list_documents(self) -> List[Dict]:
        """
        Retrieve all documents with their analysis data.
        
        Returns:
            List[Dict]: List of formatted document data for frontend
        """
        try:
            # Get documents with joined analysis data
            result = self.supabase.table("documents").select(
                "*, analysis_results(structured_data, insights)"
            ).order("upload_date", desc=True).execute()
            
            return [self._format_document_for_frontend(doc) for doc in result.data]
        except Exception as e:
            logger.error(f"Error listing documents: {e}", exc_info=True)
            raise
    
    def get_analysis(self, document_id: str) -> Optional[Dict]:
        """
        Get analysis results for a specific document.
        
        Args:
            document_id: ID of the document
            
        Returns:
            Optional[Dict]: Formatted analysis data or None if not found
        """
        try:
            # Get document with analysis data
            result = self.supabase.table("documents").select(
                "*, analysis_results(structured_data, insights)"
            ).eq("id", document_id).maybe_single().execute()
            
            if not result.data:
                return None
            
            return self._format_document_for_frontend(result.data)
        except Exception as e:
            logger.error(f"Error getting analysis for {document_id}: {e}", exc_info=True)
            return None
    
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
    
    def _format_document_for_frontend(self, doc: Dict) -> Dict:
        """
        Format document data for frontend consumption.
        
        Args:
            doc: Raw document data from database
            
        Returns:
            Dict: Formatted document data
        """
        analysis_results = doc.get("analysis_results")
        analysis = None
        
        # Handle both list (one-to-many) and dict (one-to-one) from Supabase join
        if isinstance(analysis_results, list) and len(analysis_results) > 0:
            analysis = analysis_results[0]
        elif isinstance(analysis_results, dict):
            analysis = analysis_results

        extracted_data = []
        ai_insights = None
        
        if analysis:
            structured_data = analysis.get("structured_data")
            ai_insights = analysis.get("insights")
            
            # Safely extract markers for the frontend
            if isinstance(structured_data, dict) and "data" in structured_data:
                # Ensure we handle potential missing 'markers' key gracefully
                if isinstance(structured_data["data"], dict):
                    extracted_data = structured_data["data"].get("markers", [])
        
        return {
            "id": doc.get("id"),
            "document_id": doc.get("id"),
            "filename": doc.get("filename"),
            "uploaded_at": doc.get("upload_date"),
            "status": doc.get("status"),
            "processed_at": doc.get("processed_at"),
            "public_url": doc.get("public_url"),
            "raw_text": doc.get("raw_text"),
            "extracted_data": extracted_data,
            "ai_insights": ai_insights,
            "error_message": doc.get("error_message"),
            "progress": doc.get("progress"),
            "processing_stage": doc.get("processing_stage")
        }