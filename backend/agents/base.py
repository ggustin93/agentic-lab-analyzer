"""
Agent contracts for the document processing pipeline.

The pipeline is typed against these Protocols, not against concrete vendors:
swapping an implementation (e.g. a local OCR instead of Mistral) means
providing another object with the same shape — no pipeline change, and tests
can pass plain fakes without monkeypatching.
"""

from typing import Any, Dict, Protocol

from models.health_models import HealthDataExtraction, HealthInsights


class OCRAgent(Protocol):
    """Extracts structured OCR data (pages of markdown) from a document URL."""

    def extract_structured_data(self, file_url: str) -> Dict[str, Any]:
        ...


class ExtractionAgentProtocol(Protocol):
    """Turns structured OCR data into validated health markers."""

    async def extract_data(self, structured_ocr_data: Dict[str, Any]) -> HealthDataExtraction:
        ...


class InsightAgentProtocol(Protocol):
    """Generates clinical insights from extracted health data."""

    async def generate_insights(self, extracted_data: HealthDataExtraction) -> HealthInsights:
        ...
