from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from enum import Enum

class DocumentStatus(str, Enum):
    PROCESSING = "processing"
    COMPLETE = "complete"
    ERROR = "error"

class HealthMarker(BaseModel):
    """Structured health marker extracted from medical documents"""
    marker: str = Field(description="Name of the health marker (e.g., 'Hemoglobin', 'Glucose')")
    value: str = Field(description="Measured value as string")
    unit: Optional[str] = Field(None, description="Unit of measurement (e.g., 'mg/dL', 'g/dL')")
    reference_range: Optional[str] = Field(None, description="Normal reference range")

class HealthDataExtraction(BaseModel):
    """Complete health data extraction from a medical document"""
    markers: List[HealthMarker] = Field(description="List of extracted health markers")
    document_type: str = Field(description="Type of medical document (e.g., 'Blood Test', 'Lipid Panel')")
    test_date: Optional[str] = Field(None, description="Date when tests were performed")
    patient_info: Optional[str] = Field(None, description="Patient information if available")

class HealthInsights(BaseModel):
    """AI-generated insights about health data"""
    summary: str = Field(description="Brief summary of overall health status")
    key_findings: List[str] = Field(description="List of important findings")
    recommendations: List[str] = Field(description="Health recommendations")
    risk_factors: List[str] = Field(description="Identified risk factors")
    follow_up_needed: bool = Field(description="Whether follow-up is recommended")
    disclaimer: str = Field(
        default="This analysis is for educational purposes only. Always consult healthcare professionals for medical advice.",
        description="Medical disclaimer"
    )

# API Response Models
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