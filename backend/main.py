from fastapi import FastAPI, File, UploadFile, HTTPException, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import uvicorn
import os
import logging
import json
import asyncio
from contextlib import asynccontextmanager

from services.document_processor import DocumentProcessor
from config.settings import settings # <-- MAKE SURE THIS IS IMPORTED

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize services
document_processor = DocumentProcessor()

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Health Document Analyzer API v4")
    yield
    logger.info("Shutting down Health Document Analyzer API")

app = FastAPI(
    title="Health Document Analyzer API",
    description="AI-powered health document analysis using a versioned, agent-based architecture.",
    version="4.0.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    # REPLACE the hard-coded list with the settings variable
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- API Router v1 ---
api_router_v1 = APIRouter(prefix="/api/v1")

@api_router_v1.post("/documents/upload")
async def upload_document(file: UploadFile = File(...)):
    """Uploads and begins processing of a health document."""
    try:
        # We no longer validate file type here, can be done on frontend
        # and/or inferred by content type if needed
        
        file_content = await file.read()
        document_id = await document_processor.process_document(file_content, file.filename)
        
        return {"document_id": document_id, "filename": file.filename}
        
    except Exception as e:
        logger.error(f"Upload error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@api_router_v1.get("/documents/{document_id}/stream")
async def stream_document_analysis(document_id: str):
    """Streams the analysis status of a document using SSE."""
    async def event_generator():
        while True:
            doc_data = document_processor.get_analysis(document_id)
            if doc_data:
                yield f"data: {json.dumps(doc_data)}\n\n"
                if doc_data["status"] in ["complete", "error"]:
                    break
            await asyncio.sleep(2) # Poll every 2 seconds
    return StreamingResponse(event_generator(), media_type="text/event-stream")

@api_router_v1.get("/documents")
async def list_documents():
    """List all processed documents"""
    try:
        documents = await document_processor.list_documents()
        return documents
        
    except Exception as e:
        logger.error(f"List documents error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list documents: {str(e)}")

@api_router_v1.get("/documents/{document_id}")
async def get_document(document_id: str):
    """Get a specific document by ID"""
    try:
        doc_data = document_processor.get_analysis(document_id)
        if not doc_data:
            raise HTTPException(status_code=404, detail=f"Document with ID {document_id} not found")
        return doc_data
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Get document error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get document: {str(e)}")

@api_router_v1.delete("/documents/{document_id}")
async def delete_document(document_id: str):
    """Delete a specific document and all its associated data"""
    try:
        success = await document_processor.delete_document(document_id)
        if not success:
            raise HTTPException(status_code=404, detail=f"Document with ID {document_id} not found or could not be deleted")
        return {"message": f"Document {document_id} successfully deleted", "document_id": document_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Delete document error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to delete document: {str(e)}")

@api_router_v1.post("/documents/{document_id}/retry")
async def retry_document_processing(document_id: str):
    """Retry processing for a stuck or failed document"""
    try:
        success = await document_processor.retry_document_processing(document_id)
        if not success:
            raise HTTPException(status_code=404, detail=f"Document with ID {document_id} not found or cannot be retried")
        return {"message": f"Document {document_id} processing restarted", "document_id": document_id}
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Retry document error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to retry document processing: {str(e)}")


app.include_router(api_router_v1)

# Root endpoint for basic health check
@app.get("/")
async def root():
    return {"message": "Health Document Analyzer API is running."}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)