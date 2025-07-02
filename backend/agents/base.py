from typing import Protocol
from models.health_models import HealthInsights

class OCRExtractorAgent(Protocol):
    """Defines the contract for any service that can extract text from a document."""
    async def extract_text(self, file_path: str, file_type: str) -> str:
        ...

class LabInsightAgent(Protocol):
    """Defines the contract for any service that can analyze text and return structured insights."""
    async def analyze_text(self, raw_text: str) -> HealthInsights:
        ... 