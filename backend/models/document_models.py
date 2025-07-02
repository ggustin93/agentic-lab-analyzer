from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from enum import Enum
from uuid import UUID, uuid4
from datetime import datetime

# Database Schema Models
class Document(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    filename: str
    upload_date: datetime = Field(default_factory=datetime.now)
    status: str
    user_id: Optional[UUID] = None
    storage_path: Optional[str] = None
    public_url: Optional[str] = None
    raw_text: Optional[str] = None
    error_message: Optional[str] = None
    processed_at: Optional[datetime] = None

    class Config:
        orm_mode = True

class AnalysisResult(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    document_id: UUID
    raw_text: Optional[str] = None
    structured_data: Optional[Dict] = None
    insights: Optional[str] = None

    class Config:
        orm_mode = True

class HealthMarkerDB(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    analysis_id: UUID
    marker_name: Optional[str] = None
    value: Optional[str] = None
    unit: Optional[str] = None
    reference_range: Optional[str] = None

    class Config:
        orm_mode = True

# API Response Models
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
    upload_date: str
    raw_text: Optional[str] = None
    extracted_data: List[Dict] = []
    ai_insights: Optional[str] = None
    error_message: Optional[str] = None
    processed_at: Optional[str] = None

class DocumentListItem(BaseModel):
    id: str
    filename: str
    upload_date: str
    status: str
    processed_at: Optional[str] = None