import asyncio
import uuid
import os
import json
from datetime import datetime
from typing import Dict, List, Optional
import logging

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
        self.storage_path = "data/documents"
        self.ensure_storage_directory()
    
    def ensure_storage_directory(self):
        """Ensure storage directory exists"""
        os.makedirs(self.storage_path, exist_ok=True)
    
    async def process_document(self, file_path: str, filename: str) -> str:
        """Process a document and return document ID"""
        document_id = str(uuid.uuid4())
        
        try:
            # Create document record
            document_data = {
                "id": document_id,
                "filename": filename,
                "uploaded_at": datetime.now().isoformat(),
                "status": "processing",
                "file_path": file_path
            }
            
            # Save initial document data
            await self._save_document_data(document_id, document_data)
            
            # Start background processing
            asyncio.create_task(self._process_document_async(document_id, file_path, filename))
            
            return document_id
            
        except Exception as e:
            logger.error(f"Document processing error: {e}")
            # Update status to error
            document_data["status"] = "error"
            document_data["error_message"] = str(e)
            await self._save_document_data(document_id, document_data)
            raise
    
    async def _process_document_async(self, document_id: str, file_path: str, filename: str):
        """Async processing of document with PydanticAI"""
        document_data = await self._load_document_data(document_id)
        if not document_data:
            logger.error(f"Could not load document data for {document_id}")
            return
            
        try:
            logger.info(f"Starting PydanticAI processing for document {document_id}")
            
            file_type = filename.split('.')[-1].lower()
            raw_text = self.ocr_agent.extract_text(file_path, file_type)
            if not raw_text.strip():
                raise ValueError("OCR process yielded no text.")
            
            insights_result = await self.insight_agent.analyze_text(raw_text)
            
            # Format for storage and response
            document_data.update({
                "status": "complete",
                "raw_text": raw_text,
                "extracted_data": [marker.model_dump() for marker in insights_result.data.markers],
                "ai_insights": self._format_insights_as_markdown(insights_result),
                "processed_at": datetime.now().isoformat()
            })
            
            await self._save_document_data(document_id, document_data)
            logger.info(f"Successfully processed document {document_id} with PydanticAI")
            
        except Exception as e:
            logger.error(f"Async processing error for document {document_id}: {e}", exc_info=True)
            document_data["status"] = "error"
            document_data["error_message"] = str(e)
            await self._save_document_data(document_id, document_data)

    def _format_insights_as_markdown(self, insights: HealthInsights) -> str:
        # Helper function to convert the structured insights object to a single markdown string for the frontend
        md = f"# Analysis Report\n\n## Summary\n{insights.summary}\n\n"
        md += "## Key Findings\n" + "".join([f"- {finding}\n" for finding in insights.key_findings])
        md += "\n## Recommendations\n" + "".join([f"- {rec}\n" for rec in insights.recommendations])
        md += f"\n---\n\n**Disclaimer:** {insights.disclaimer}"
        return md

    async def get_analysis(self, document_id: str) -> Optional[Dict]:
        """Get analysis results for a document"""
        try:
            document_data = await self._load_document_data(document_id)
            if not document_data:
                return None
            
            return {
                "document_id": document_id,
                "status": document_data["status"],
                "filename": document_data["filename"],
                "uploaded_at": document_data["uploaded_at"],
                "raw_text": document_data.get("raw_text"),
                "extracted_data": document_data.get("extracted_data", []),
                "ai_insights": document_data.get("ai_insights"),
                "error_message": document_data.get("error_message"),
                "processed_at": document_data.get("processed_at")
            }
            
        except Exception as e:
            logger.error(f"Error retrieving analysis for {document_id}: {e}")
            return None
    
    async def delete_document(self, document_id: str) -> bool:
        """Delete a document and its data"""
        try:
            document_path = os.path.join(self.storage_path, f"{document_id}.json")
            
            # Load document data to get file path
            document_data = await self._load_document_data(document_id)
            
            # Delete document file if it exists
            if document_data and "file_path" in document_data:
                file_path = document_data["file_path"]
                if os.path.exists(file_path):
                    os.remove(file_path)
            
            # Delete document data
            if os.path.exists(document_path):
                os.remove(document_path)
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error deleting document {document_id}: {e}")
            return False
    
    async def list_documents(self) -> List[Dict]:
        """List all processed documents"""
        try:
            documents = []
            
            for filename in os.listdir(self.storage_path):
                if filename.endswith('.json'):
                    document_id = filename[:-5]  # Remove .json extension
                    document_data = await self._load_document_data(document_id)
                    
                    if document_data:
                        documents.append({
                            "id": document_data["id"],
                            "filename": document_data["filename"],
                            "uploaded_at": document_data["uploaded_at"],
                            "status": document_data["status"],
                            "processed_at": document_data.get("processed_at")
                        })
            
            # Sort by upload date (newest first)
            documents.sort(key=lambda x: x["uploaded_at"], reverse=True)
            return documents
            
        except Exception as e:
            logger.error(f"Error listing documents: {e}")
            return []
    
    async def _save_document_data(self, document_id: str, data: Dict):
        """Save document data to storage"""
        try:
            document_path = os.path.join(self.storage_path, f"{document_id}.json")
            with open(document_path, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving document data for {document_id}: {e}")
            raise
    
    async def _load_document_data(self, document_id: str) -> Optional[Dict]:
        """Load document data from storage"""
        try:
            document_path = os.path.join(self.storage_path, f"{document_id}.json")
            if os.path.exists(document_path):
                with open(document_path, 'r') as f:
                    return json.load(f)
            return None
        except Exception as e:
            logger.error(f"Error loading document data for {document_id}: {e}")
            return None