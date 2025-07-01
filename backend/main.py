"""
Ultra-Simple MVP API
No database, essential endpoints only
"""

from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import logging
from contextlib import asynccontextmanager

from services.document_processor import DocumentProcessor
from services.ocr_service import OCRService
from services.ai_service import AIService
from models.health_models import DocumentResponse
from utils.file_handler import FileHandler
from config.settings import settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize services
document_processor = DocumentProcessor()
ocr_service = OCRService()
ai_service = AIService()
file_handler = FileHandler()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 Starting Health Document Analyzer - Ultra-Simple MVP")
    logger.info(f"📊 Chutes.ai available: {ai_service.is_available()}")
    logger.info(f"🔍 Mistral OCR available: {ocr_service.is_available()}")
    
    if not settings.is_configured():
        logger.warning("⚠️  Cloud services not fully configured")
    else:
        logger.info("✅ All services configured")
    
    yield
    # Shutdown
    logger.info("👋 Shutting down")

app = FastAPI(
    title="Health Document Analyzer - Ultra-Simple MVP",
    description="Essential cloud-only health document analysis",
    version="1.0.0-mvp",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.get_cors_origins_list(),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "Health Document Analyzer - Ultra-Simple MVP", 
        "status": "running",
        "services": {
            "ai": "Chutes.ai + Deepseek",
            "ocr": "Mistral OCR",
            "storage": "In-Memory (No Database)"
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "services": {
            "ocr_available": ocr_service.is_available(),
            "ai_available": ai_service.is_available(),
            "fully_configured": settings.is_configured()
        }
    }

@app.post("/api/upload", response_model=DocumentResponse)
async def upload_document(file: UploadFile = File(...)):
    """Upload and process document"""
    try:
        # Check configuration
        if not settings.is_configured():
            raise HTTPException(
                status_code=503, 
                detail="Services not configured. Check CHUTES_API_TOKEN and MISTRAL_API_KEY."
            )
        
        # Validate file
        if not file_handler.is_valid_file(file):
            raise HTTPException(status_code=400, detail="Invalid file type or size")
        
        # Save file
        file_path = await file_handler.save_upload(file)
        
        # Process document
        document_id = await document_processor.process_document(file_path, file.filename)
        
        return DocumentResponse(
            document_id=document_id,
            message="Document uploaded and processing started",
            status="processing"
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Upload error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/document/{document_id}")
async def get_document_analysis(document_id: str):
    """Get analysis results"""
    try:
        analysis = await document_processor.get_analysis(document_id)
        if not analysis:
            raise HTTPException(status_code=404, detail="Document not found")
        return analysis
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/api/document/{document_id}")
async def delete_document(document_id: str):
    """Delete document"""
    try:
        success = await document_processor.delete_document(document_id)
        if not success:
            raise HTTPException(status_code=404, detail="Document not found")
        return {"message": "Document deleted"}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/documents")
async def list_documents():
    """List all documents"""
    try:
        documents = await document_processor.list_documents()
        return {"documents": documents}
    except Exception as e:
        logger.error(f"List error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# Test endpoint for demo
@app.post("/api/test")
async def test_services():
    """Test cloud services"""
    try:
        if not settings.is_configured():
            return {
                "status": "not_configured",
                "message": "Configure CHUTES_API_TOKEN and MISTRAL_API_KEY to test services"
            }
        
        # Test AI with sample data
        test_text = "Hemoglobin: 14.5 g/dL (Reference: 13.5-17.5)\nGlucose: 95 mg/dL (Reference: 70-99)"
        
        health_data = await ai_service.extract_health_data(
            raw_text=test_text,
            filename="test.txt"
        )
        
        insights = await ai_service.generate_insights(
            health_data=health_data,
            raw_text=test_text,
            filename="test.txt"
        )
        
        return {
            "status": "success",
            "ai_service": "working",
            "ocr_service": "available" if ocr_service.is_available() else "unavailable",
            "test_results": {
                "extracted_markers": len(health_data.markers),
                "insights_generated": bool(insights.summary)
            }
        }
        
    except Exception as e:
        logger.error(f"Test error: {e}")
        return {
            "status": "error",
            "message": str(e)
        }

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level=settings.log_level.lower()
    )