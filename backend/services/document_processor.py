"""
Ultra-Simple Document Processor - No Database
In-memory storage for MVP demonstration
"""

import asyncio
import uuid
import os
import json
from datetime import datetime
from typing import Dict, List, Optional
import logging

from .ocr_service import OCRService
from .ai_service import AIService
from models.health_models import DocumentStatus

logger = logging.getLogger(__name__)

class DocumentProcessor:
    """Simple in-memory document processor for MVP"""
    
    def __init__(self):
        self.ocr_service = OCRService()
        self.ai_service = AIService()
        
        # In-memory storage for MVP
        self.documents: Dict[str, Dict] = {}
        
        # Ensure upload directory exists
        os.makedirs("uploads", exist_ok=True)
    
    async def process_document(self, file_path: str, filename: str) -> str:
        """Process document and return document ID"""
        document_id = str(uuid.uuid4())
        
        # Store initial document info
        self.documents[document_id] = {
            "id": document_id,
            "filename": filename,
            "uploaded_at": datetime.now().isoformat(),
            "status": DocumentStatus.PROCESSING.value,
            "file_path": file_path
        }
        
        # Start background processing
        asyncio.create_task(self._process_document_async(document_id, file_path, filename))
        
        return document_id
    
    async def _process_document_async(self, document_id: str, file_path: str, filename: str):
        """Background processing"""
        try:
            logger.info(f"Processing document {document_id}")
            
            # Extract file type
            file_extension = filename.split('.')[-1].lower()
            
            # Step 1: OCR
            logger.info(f"Extracting text from {filename}")
            raw_text = await self.ocr_service.extract_text(file_path, file_extension)
            
            if not raw_text.strip():
                raise Exception("No text extracted")
            
            # Step 2: AI Analysis
            logger.info(f"Analyzing health data for {document_id}")
            health_data = await self.ai_service.extract_health_data(
                raw_text=raw_text,
                filename=filename,
                document_type=self._infer_document_type(filename, raw_text)
            )
            
            # Step 3: Generate Insights
            logger.info(f"Generating insights for {document_id}")
            insights = await self.ai_service.generate_insights(
                health_data=health_data,
                raw_text=raw_text,
                filename=filename
            )
            
            # Convert to frontend format
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
            
            # Update document with results
            self.documents[document_id].update({
                "status": DocumentStatus.COMPLETE.value,
                "raw_text": raw_text,
                "extracted_data": extracted_data,
                "ai_insights": ai_insights,
                "processed_at": datetime.now().isoformat()
            })
            
            logger.info(f"Successfully processed document {document_id}")
            
        except Exception as e:
            logger.error(f"Processing error for {document_id}: {e}")
            self.documents[document_id].update({
                "status": DocumentStatus.ERROR.value,
                "error_message": str(e)
            })
        finally:
            # Clean up uploaded file
            try:
                if os.path.exists(file_path):
                    os.remove(file_path)
            except Exception as e:
                logger.warning(f"Failed to clean up file {file_path}: {e}")
    
    def _infer_document_type(self, filename: str, raw_text: str) -> str:
        """Simple document type inference"""
        filename_lower = filename.lower()
        text_lower = raw_text.lower()
        
        if any(term in filename_lower or term in text_lower for term in ['blood', 'cbc', 'hemoglobin']):
            return "Blood Test"
        elif any(term in filename_lower or term in text_lower for term in ['lipid', 'cholesterol']):
            return "Lipid Panel"
        elif any(term in filename_lower or term in text_lower for term in ['glucose', 'diabetes']):
            return "Diabetes Panel"
        else:
            return "Health Report"
    
    def _format_insights_as_markdown(self, insights) -> str:
        """Format insights as markdown"""
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
            markdown += "Consider discussing these results with your healthcare provider.\n"
        
        markdown += f"\n## Important Disclaimer\n"
        markdown += f"⚠️ **{insights.disclaimer}**\n"
        
        return markdown
    
    async def get_analysis(self, document_id: str) -> Optional[Dict]:
        """Get document analysis"""
        if document_id not in self.documents:
            return None
        
        doc = self.documents[document_id]
        return {
            "document_id": document_id,
            "status": doc["status"],
            "filename": doc["filename"],
            "uploaded_at": doc["uploaded_at"],
            "raw_text": doc.get("raw_text"),
            "extracted_data": doc.get("extracted_data", []),
            "ai_insights": doc.get("ai_insights"),
            "error_message": doc.get("error_message"),
            "processed_at": doc.get("processed_at")
        }
    
    async def delete_document(self, document_id: str) -> bool:
        """Delete document"""
        if document_id in self.documents:
            del self.documents[document_id]
            return True
        return False
    
    async def list_documents(self) -> List[Dict]:
        """List all documents"""
        documents = []
        for doc_id, doc in self.documents.items():
            documents.append({
                "id": doc_id,
                "filename": doc["filename"],
                "uploaded_at": doc["uploaded_at"],
                "status": doc["status"],
                "processed_at": doc.get("processed_at")
            })
        
        # Sort by upload date (newest first)
        documents.sort(key=lambda x: x["uploaded_at"], reverse=True)
        return documents