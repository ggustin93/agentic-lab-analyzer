# backend/models/health_models.py

from pydantic import BaseModel, Field
from typing import List, Optional, Union
from enum import Enum
from datetime import datetime

# ====================================================================
# NEW MODELS FOR THE 3-AGENT PIPELINE
# ====================================================================

class MarkerStatus(str, Enum):
    """Enumeration for the status of a health marker's value."""
    DANGER_LOW = "danger_low"
    WARNING_LOW = "warning_low"
    NORMAL = "normal"
    WARNING_HIGH = "warning_high"
    DANGER_HIGH = "danger_high"
    UNKNOWN = "unknown" # Use when comparison isn't possible

# --- Agent 2: Data Extractor Agent (LLM Output) ---
class ExtractedHealthMarker(BaseModel):
    """Defines the raw data extracted directly from the text by the LLM."""
    marker: str = Field(..., description="Name of the health marker, e.g., 'Hemoglobin'")
    value: str = Field(..., description="The measured value as a string, e.g., '14.5'")
    unit: Optional[str] = Field(None, description="Unit of measurement, e.g., 'g/dL'")
    reference_range: Optional[str] = Field(None, description="The normal reference range as a string, e.g., '13.5 - 17.5'")

class ExtractedHealthData(BaseModel):
    """The complete structured output from the Data Extractor's LLM call."""
    markers: List[ExtractedHealthMarker] = Field(..., description="A list of all extracted health markers.")
    document_type: str = Field(..., description="The inferred type of document, e.g., 'Blood Test Report'")
    test_date: Optional[str] = Field(None, description="The date the test was performed, as a string e.g., 'MM/DD/YYYY'")


# --- Agent 2: Data Extractor Agent (Final Python Output) ---
class AnalyzedHealthMarker(ExtractedHealthMarker):
    """Enriches the extracted marker with a calculated status."""
    status: MarkerStatus = Field(MarkerStatus.UNKNOWN, description="The status of the marker relative to its reference range.")

class AnalyzedHealthData(BaseModel):
    """The final, analyzed output from the Data Extractor Agent, ready for the next agent."""
    markers: List[AnalyzedHealthMarker]
    document_type: str
    test_date: Optional[str]

# --- Agent 3: Clinical Insight Agent (Final Output) ---
class HealthInsights(BaseModel):
    """
    The final, combined output of the entire analysis pipeline.
    This model structures the data for the frontend UI.
    """
    data: AnalyzedHealthData = Field(..., description="The structured and analyzed data from the document.")
    summary: str = Field(..., description="A brief, high-level summary of the findings, written for a layperson.")
    key_findings: List[str] = Field(..., description="A bulleted list of the most important findings, focusing on out-of-range markers.")
    recommendations: List[str] = Field(..., description="A bulleted list of general, non-prescriptive lifestyle and dietary recommendations.")
    disclaimer: str = Field(..., description="A non-negotiable medical disclaimer.") 