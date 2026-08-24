from fastapi import FastAPI, File, Request, UploadFile, HTTPException, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import uvicorn
import logging
import json
import asyncio
import magic
from contextlib import asynccontextmanager

from services.document_processor import DocumentProcessor
from config.settings import settings

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize services
document_processor = DocumentProcessor()

# Content types accepted for upload, verified from magic bytes — never from
# the filename or the client-declared content type (backlog 001)
ALLOWED_UPLOAD_MIME_TYPES = {"application/pdf", "image/png", "image/jpeg"}

# SSE streams are bounded: without this, a stream for a document stuck in
# "processing" would poll the database forever (backlog 002)
SSE_POLL_INTERVAL_SECONDS = 2
SSE_MAX_LIFETIME_SECONDS = 15 * 60

# Client-facing messages are generic by design: exception details go to the
# server logs only (backlog 006)
GENERIC_ERROR_MESSAGES = {
    "upload": "Upload failed. Please try again.",
    "list": "Failed to list documents. Please try again.",
    "get": "Failed to retrieve the document. Please try again.",
    "delete": "Failed to delete the document. Please try again.",
    "retry": "Failed to restart processing. Please try again.",
}


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting Health Document Analyzer API v4")
    yield
    await document_processor.processing_pipeline.aclose()
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
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- API Router v1 ---
api_router_v1 = APIRouter(prefix="/api/v1")


async def _read_validated_upload(file: UploadFile) -> bytes:
    """
    Read an upload with server-side validation: bounded size (chunked read,
    so an oversized body is never fully buffered) and magic-bytes content
    type. Raises typed HTTP errors; a rejected file leaves no trace.
    """
    max_size = settings.MAX_FILE_SIZE
    chunks = []
    total = 0
    while True:
        chunk = await file.read(1024 * 1024)
        if not chunk:
            break
        total += len(chunk)
        if total > max_size:
            raise HTTPException(
                status_code=413,
                detail=f"File exceeds the maximum size of {max_size // (1024 * 1024)} MB."
            )
        chunks.append(chunk)

    file_content = b"".join(chunks)
    if not file_content:
        raise HTTPException(status_code=415, detail="Empty file.")

    mime_type = magic.from_buffer(file_content[:8192], mime=True)
    if mime_type not in ALLOWED_UPLOAD_MIME_TYPES:
        raise HTTPException(
            status_code=415,
            detail="Unsupported file type. Accepted formats: PDF, PNG, JPEG."
        )

    return file_content


@api_router_v1.post("/documents/upload", status_code=202)
async def upload_document(file: UploadFile = File(...)):
    """Uploads and begins processing of a health document."""
    file_content = await _read_validated_upload(file)
    try:
        document_id = await document_processor.process_document(file_content, file.filename)
        return {"document_id": document_id, "filename": file.filename}
    except Exception as e:
        logger.error(f"Upload error: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=GENERIC_ERROR_MESSAGES["upload"])


@api_router_v1.get("/documents/{document_id}/stream")
async def stream_document_analysis(document_id: str, request: Request):
    """Streams the analysis status of a document using SSE."""
    if document_processor.get_analysis(document_id) is None:
        raise HTTPException(status_code=404, detail=f"Document with ID {document_id} not found")

    async def event_generator():
        max_polls = SSE_MAX_LIFETIME_SECONDS // SSE_POLL_INTERVAL_SECONDS
        for _ in range(max_polls):
            if await request.is_disconnected():
                return
            doc_data = document_processor.get_analysis(document_id)
            if doc_data:
                yield f"data: {json.dumps(doc_data)}\n\n"
                if doc_data["status"] in ["complete", "error"]:
                    return
            await asyncio.sleep(SSE_POLL_INTERVAL_SECONDS)
        # Lifetime bound reached: close explicitly rather than poll forever
        yield "event: timeout\ndata: {}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


@api_router_v1.get("/documents")
async def list_documents():
    """List all processed documents"""
    try:
        documents = await document_processor.list_documents()
        return documents
    except Exception as e:
        logger.error(f"List documents error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=GENERIC_ERROR_MESSAGES["list"])


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
        logger.error(f"Get document error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=GENERIC_ERROR_MESSAGES["get"])


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
        logger.error(f"Delete document error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=GENERIC_ERROR_MESSAGES["delete"])


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
        logger.error(f"Retry document error: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=GENERIC_ERROR_MESSAGES["retry"])


app.include_router(api_router_v1)


# Root endpoint for basic health check
@app.get("/")
async def root():
    return {"message": "Health Document Analyzer API is running."}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
