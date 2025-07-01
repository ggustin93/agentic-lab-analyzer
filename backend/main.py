from fastapi import FastAPI, File, UploadFile, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import uvicorn
import os
from dotenv import load_dotenv
import logging
from contextlib import asynccontextmanager

# Import PydanticAI and Logfire for monitoring
try:
    import logfire
    logfire.configure()
    LOGFIRE_AVAILABLE = True
except ImportError:
    LOGFIRE_AVAILABLE = False
    logging.warning("Logfire not available - monitoring disabled")

from services.document_processor import DocumentProcessor
from services.ocr_service import OCRService
from agents.health_analysis_agent import HealthAnalysisService
from models.health_models import DocumentResponse, AnalysisResponse
from utils.file_handler import FileHandler

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize services
document_processor = DocumentProcessor()
ocr_service = OCRService()
health_analysis_service = HealthAnalysisService()
file_handler = FileHandler()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Health Document Analyzer API with PydanticAI")
    if LOGFIRE_AVAILABLE:
        logger.info("Logfire monitoring enabled")
    yield
    # Shutdown
    logger.info("Shutting down Health Document Analyzer API")

app = FastAPI(
    title="Health Document Analyzer API",
    description="AI-powered health document analysis using PydanticAI, OCR and LLM",
    version="2.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "Health Document Analyzer API v2.0", 
        "status": "running",
        "powered_by": "PydanticAI",
        "monitoring": "Logfire" if LOGFIRE_AVAILABLE else "Basic logging"
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy", 
        "services": {
            "ocr": ocr_service.is_available(),
            "health_analysis": health_analysis_service.is_available(),
            "logfire": LOGFIRE_AVAILABLE
        }
    }

@app.post("/api/upload", response_model=DocumentResponse)
async def upload_document(file: UploadFile = File(...)):
    """Upload and process a health document with PydanticAI"""
    try:
        # Validate file
        if not file_handler.is_valid_file(file):
            raise HTTPException(status_code=400, detail="Invalid file type or size")
        
        # Save uploaded file
        file_path = await file_handler.save_upload(file)
        
        # Process document with PydanticAI
        document_id = await document_processor.process_document(file_path, file.filename)
        
        return DocumentResponse(
            document_id=document_id,
            message="Document uploaded and processing started with PydanticAI",
            status="processing"
        )
        
    except Exception as e:
        logger.error(f"Upload error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@app.get("/api/document/{document_id}")
async def get_document_analysis(document_id: str):
    """Get analysis results for a document"""
    try:
        analysis = await document_processor.get_analysis(document_id)
        if not analysis:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return analysis
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Analysis retrieval error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retrieve analysis: {str(e)}")

@app.delete("/api/document/{document_id}")
async def delete_document(document_id: str):
    """Delete a document and its analysis"""
    try:
        success = await document_processor.delete_document(document_id)
        if not success:
            raise HTTPException(status_code=404, detail="Document not found")
        
        return {"message": "Document deleted successfully"}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete document: {str(e)}")

@app.get("/api/documents")
async def list_documents():
    """List all processed documents"""
    try:
        documents = await document_processor.list_documents()
        return {"documents": documents}
        
    except Exception as e:
        logger.error(f"List documents error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list documents: {str(e)}")

# New endpoint for testing PydanticAI directly
@app.post("/api/test-analysis")
async def test_health_analysis(text: str):
    """Test endpoint for PydanticAI health analysis"""
    try:
        # Extract health data
        health_data = await health_analysis_service.extract_health_data(
            raw_text=text,
            filename="test_document.txt"
        )
        
        # Generate insights
        insights = await health_analysis_service.generate_insights(
            health_data=health_data,
            raw_text=text,
            filename="test_document.txt"
        )
        
        return {
            "extracted_data": health_data.model_dump(),
            "insights": insights.model_dump()
        }
        
    except Exception as e:
        logger.error(f"Test analysis error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )