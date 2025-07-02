from pydantic import BaseModel
from typing import List, Optional, Dict
from enum import Enum

class DocumentStatus(str, Enum):
    PROCESSING = "processing"
    COMPLETE = "complete"
    ERROR = "error"

class HealthMarker(BaseModel):
    marker: str
    value: str
    unit: Optional[str] = None
    referenceRange: Optional[str] = None

class DocumentResponse(BaseModel):
    document_id: str
    message: str
    status: str

class AnalysisResponse(BaseModel):
    document_id: str
    status: str
    filename: str
    uploaded_at: str
    raw_text: Optional[str] = None
    extracted_data: List[Dict] = []
    ai_insights: Optional[str] = None
    error_message: Optional[str] = None
    processed_at: Optional[str] = None

class DocumentListItem(BaseModel):
    id: str
    filename: str
    uploaded_at: str
    status: str
    processed_at: Optional[str] = None