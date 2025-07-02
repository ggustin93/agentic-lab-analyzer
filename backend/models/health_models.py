from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

class HealthMarker(BaseModel):
    marker: str = Field(..., description="Name of the health marker, e.g., 'Hemoglobin'")
    value: str = Field(..., description="The measured value as a string.")
    unit: Optional[str] = Field(None, description="Unit of measurement, e.g., 'g/dL'")
    reference_range: Optional[str] = Field(None, description="The normal reference range, e.g., '13.5 - 17.5'")

class HealthDataExtraction(BaseModel):
    markers: List[HealthMarker] = Field(..., description="A list of all extracted health markers.")
    document_type: str = Field(..., description="The inferred type of document, e.g., 'Blood Test Report'")
    test_date: Optional[datetime] = Field(None, description="The date the test was performed.")

class HealthInsights(BaseModel):
    data: HealthDataExtraction = Field(..., description="The structured data extracted from the document.")
    summary: str = Field(..., description="A brief, high-level summary of the findings.")
    key_findings: List[str] = Field(..., description="A bulleted list of the most important findings.")
    recommendations: List[str] = Field(..., description="A bulleted list of general, non-prescriptive recommendations.")
    disclaimer: str = Field(..., description="A non-negotiable medical disclaimer.") 