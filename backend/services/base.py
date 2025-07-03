from typing import Protocol

class OCRExtractorAgent(Protocol):
    """Defines the contract for any service that can extract text from a document."""
    async def extract_text(self, file_path: str, file_type: str) -> str:
        ... 