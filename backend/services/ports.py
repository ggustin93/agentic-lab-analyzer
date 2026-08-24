"""
Persistence ports (ADR-008).

Protocol contracts for the two infrastructure seams the processing workflow
depends on: document persistence and file storage. Mirrors the public surface
of the original Supabase-backed managers — including their sync/async
asymmetry — so both adapters (local SQLite / Supabase) are drop-in
substitutes and tests can use plain fakes, following the same pattern as the
agent contracts in agents/base.py (ADR-007).
"""

from typing import Dict, List, Optional, Protocol


class DocumentRepository(Protocol):
    """Persistence operations for documents, analyses and health markers."""

    def create_document_record(self, document_id: str, filename: str, storage_path: str, public_url: str) -> None: ...

    def update_processing_stage(self, document_id: str, stage: str, extra_data: Optional[Dict] = None) -> None: ...

    def mark_document_error(self, document_id: str, error_message: str) -> None: ...

    def update_document_raw_text(self, document_id: str, raw_text: str) -> None: ...

    def update_document_table(self, document_id: str, data: Dict) -> None: ...

    def save_analysis_results(self, document_id: str, analysis_data: Dict) -> None: ...

    async def delete_analysis_data(self, document_id: str) -> None: ...

    def load_document_data(self, document_id: str) -> Optional[Dict]: ...

    def delete_document_record(self, document_id: str) -> None: ...

    async def list_documents(self) -> List[Dict]: ...

    def get_analysis(self, document_id: str) -> Optional[Dict]: ...


class FileStorage(Protocol):
    """File storage operations for uploaded documents."""

    def upload_file(self, file_content: bytes, storage_path: str) -> str: ...

    async def delete_file(self, storage_path: Optional[str]) -> None: ...

    async def delete_file_with_retry(self, storage_path: str, max_retries: int = 3) -> None: ...
