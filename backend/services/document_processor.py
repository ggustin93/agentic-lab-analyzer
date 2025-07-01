import asyncio
import uuid
import os
import json
from datetime import datetime
from typing import Dict, List, Optional
import logging

from .ocr_service import OCRService
from agents.health_analysis_agent import HealthAnalysisService
from models.health_models import DocumentStatus, HealthDataExtraction, HealthInsights

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Main service for processing health documents with PydanticAI"""
    
    def __init__(self):
        self.ocr_service = OCRService()
        self.health_analysis_service = HealthAnalysisService()
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
                "status": DocumentStatus.PROCESSING.value,
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
            document_data["status"] = DocumentStatus.ERROR.value
            document_data["error_message"] = str(e)
            await self._save_document_data(document_id, document_data)
            raise
    
    async def _process_document_async(self, document_id: str, file_path: str, filename: str):
        """Async processing of document with PydanticAI"""
        try:
            logger.info(f"Starting PydanticAI processing for document {document_id}")
            
            # Extract file type
            file_extension = filename.split('.')[-1].lower()
            
            # Step 1: OCR - Extract text
            logger.info(f"Extracting text from {filename}")
            raw_text = await self.ocr_service.extract_text(file_path, file_extension)
            
            if not raw_text.strip():
                raise Exception("No text could be extracted from the document")
            
            # Step 2: PydanticAI - Extract structured health data
            logger.info(f"Extracting structured health data for document {document_id}")
            health_data: HealthDataExtraction = await self.health_analysis_service.extract_health_data(
                raw_text=raw_text,
                filename=filename,
                document_type=self._infer_document_type(filename, raw_text)
            )
            
            # Step 3: PydanticAI - Generate insights
            logger.info(f"Generating health insights for document {document_id}")
            insights: HealthInsights = await self.health_analysis_service.generate_insights(
                health_data=health_data,
                raw_text=raw_text,
                filename=filename
            )
            
            # Step 4: Convert to legacy format for frontend compatibility
            extracted_data = [
                {
                    "marker": marker.marker,
                    "value": marker.value,
                    "unit": marker.unit,
                    "referenceRange": marker.reference_range
                }
                for marker in health_data.markers
            ]
            
            # Format insights as markdown
            ai_insights = self._format_insights_as_markdown(insights)
            
            # Step 5: Save results
            document_data = {
                "id": document_id,
                "filename": filename,
                "uploaded_at": datetime.now().isoformat(),
                "status": DocumentStatus.COMPLETE.value,
                "file_path": file_path,
                "raw_text": raw_text,
                "extracted_data": extracted_data,
                "ai_insights": ai_insights,
                "processed_at": datetime.now().isoformat(),
                # Store structured data for future use
                "structured_health_data": health_data.model_dump(),
                "structured_insights": insights.model_dump()
            }
            
            await self._save_document_data(document_id, document_data)
            logger.info(f"Successfully processed document {document_id} with PydanticAI")
            
        except Exception as e:
            logger.error(f"Async processing error for document {document_id}: {e}")
            
            # Update status to error
            document_data = await self._load_document_data(document_id)
            if document_data:
                document_data["status"] = DocumentStatus.ERROR.value
                document_data["error_message"] = str(e)
                await self._save_document_data(document_id, document_data)
    
    def _infer_document_type(self, filename: str, raw_text: str) -> str:
        """Infer document type from filename and content"""
        filename_lower = filename.lower()
        text_lower = raw_text.lower()
        
        if any(term in filename_lower or term in text_lower for term in ['blood', 'cbc', 'hemoglobin']):
            return "Blood Test"
        elif any(term in filename_lower or term in text_lower for term in ['lipid', 'cholesterol', 'triglyceride']):
            return "Lipid Panel"
        elif any(term in filename_lower or term in text_lower for term in ['glucose', 'diabetes', 'hba1c']):
            return "Diabetes Panel"
        elif any(term in filename_lower or term in text_lower for term in ['thyroid', 'tsh', 't3', 't4']):
            return "Thyroid Function"
        else:
            return "General Health Report"
    
    def _format_insights_as_markdown(self, insights: HealthInsights) -> str:
        """Format structured insights as markdown for frontend display"""
        markdown = f"""# Health Analysis Report

## Summary
{insights.summary}

## Key Findings
"""
        for finding in insights.key_findings:
            markdown += f"- {finding}\n"
        
        if insights.risk_factors:
            markdown += "\n## Risk Factors\n"
            for risk in insights.risk_factors:
                markdown += f"- ⚠️ {risk}\n"
        
        markdown += "\n## Recommendations\n"
        for rec in insights.recommendations:
            markdown += f"- {rec}\n"
        
        if insights.follow_up_needed:
            markdown += "\n## Follow-up Recommended\n"
            markdown += "Based on the analysis, follow-up with your healthcare provider is recommended.\n"
        
        markdown += f"\n## Important Disclaimer\n"
        markdown += f"⚠️ **{insights.disclaimer}**\n"
        
        return markdown
    
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