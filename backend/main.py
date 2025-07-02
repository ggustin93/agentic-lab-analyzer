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
from utils.file_handler import FileHandler

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize services
document_processor = DocumentProcessor()
file_handler = FileHandler()

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
    allow_origins=["http://localhost:4200"],
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
        if not file_handler.is_valid_file(file):
            raise HTTPException(status_code=400, detail="Invalid file type or size.")
        
        file_path = await file_handler.save_upload(file)
        document_id = await document_processor.process_document(file_path, file.filename)
        
        return {"document_id": document_id, "filename": file.filename}
        
    except Exception as e:
        logger.error(f"Upload error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")

@api_router_v1.get("/documents/{document_id}/stream")
async def stream_document_analysis(document_id: str):
    """Streams the analysis status of a document using SSE."""
    async def event_generator():
        while True:
            doc_data = await document_processor.get_analysis(document_id)
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


app.include_router(api_router_v1)

# Root endpoint for basic health check
@app.get("/")
async def root():
    return {"message": "Health Document Analyzer API is running."}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)