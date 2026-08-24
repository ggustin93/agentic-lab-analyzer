"""
Contract tests for the local persistence adapters (ADR-008).

These run against a real SQLite database and a real temp directory — no
mocks — proving that LocalDatabaseManager and LocalStorageManager honor the
DocumentRepository / FileStorage ports the pipeline depends on. The Supabase
adapters keep their mocked coverage elsewhere: contract-testing a MagicMock
proves nothing.
"""

import pytest

from services.local_database_manager import LocalDatabaseManager
from services.local_storage_manager import LocalStorageManager


@pytest.fixture
def db(tmp_path):
    return LocalDatabaseManager(str(tmp_path / "test.db"))


@pytest.fixture
def storage(tmp_path):
    return LocalStorageManager(str(tmp_path / "uploads"))


ANALYSIS_DATA = {
    "data": {
        "markers": [
            {"marker": "Hemoglobin", "value": 14.2, "unit": "g/dL",
             "reference_range": "13.0 - 17.5", "is_out_of_range": False},
            {"marker": "Glucose", "value": 108, "unit": "mg/dL",
             "reference_range": "70 - 99", "is_out_of_range": True},
        ],
        "document_type": "Blood Test Report",
        "test_date": "2025-07-12",
    },
    "summary": "A summary.",
    "key_findings": ["Glucose above range."],
    "recommendations": ["Consult a professional."],
    "disclaimer": "Not medical advice.",
}


def _create_doc(db, doc_id="doc-1"):
    db.create_document_record(doc_id, "report.pdf", f"{doc_id}.pdf", f"http://localhost:8000/api/v1/files/{doc_id}.pdf")
    return doc_id


class TestLocalDatabaseManager:
    def test_create_and_load_document(self, db):
        doc_id = _create_doc(db)
        row = db.load_document_data(doc_id)
        assert row["filename"] == "report.pdf"
        assert row["status"] == "processing"
        assert row["upload_date"]  # ISO timestamp present

    def test_load_missing_document_returns_none(self, db):
        assert db.load_document_data("nope") is None

    def test_update_processing_stage_sets_progress(self, db):
        doc_id = _create_doc(db)
        db.update_processing_stage(doc_id, "ai_analysis", {"progress": 30})
        row = db.load_document_data(doc_id)
        assert row["processing_stage"] == "ai_analysis"
        assert row["progress"] == 30

    def test_mark_document_error(self, db):
        doc_id = _create_doc(db)
        db.mark_document_error(doc_id, "boom")
        row = db.load_document_data(doc_id)
        assert row["status"] == "error"
        assert row["error_message"] == "boom"

    def test_update_document_table_complete_sets_processed_at(self, db):
        doc_id = _create_doc(db)
        db.update_document_table(doc_id, {"status": "complete", "progress": 100, "processing_stage": "complete"})
        row = db.load_document_data(doc_id)
        assert row["status"] == "complete"
        assert row["processed_at"] is not None

    def test_save_analysis_results_and_get_analysis(self, db):
        doc_id = _create_doc(db)
        db.update_document_raw_text(doc_id, "raw ocr text")
        db.save_analysis_results(doc_id, ANALYSIS_DATA)

        analysis = db.get_analysis(doc_id)
        assert analysis["document_id"] == doc_id
        assert len(analysis["extracted_data"]) == 2
        assert analysis["extracted_data"][1]["is_out_of_range"] is True
        assert "Disclaimer" in analysis["ai_insights"]

    def test_save_analysis_results_upsert_is_idempotent(self, db):
        doc_id = _create_doc(db)
        db.save_analysis_results(doc_id, ANALYSIS_DATA)
        db.save_analysis_results(doc_id, ANALYSIS_DATA)  # second run must not duplicate

        docs_sync = db.get_analysis(doc_id)
        assert len(docs_sync["extracted_data"]) == 2

    @pytest.mark.asyncio
    async def test_list_documents_orders_and_joins(self, db):
        _create_doc(db, "doc-a")
        _create_doc(db, "doc-b")
        db.save_analysis_results("doc-a", ANALYSIS_DATA)

        docs = await db.list_documents()
        assert len(docs) == 2
        by_id = {d["document_id"]: d for d in docs}
        assert len(by_id["doc-a"]["extracted_data"]) == 2
        assert by_id["doc-b"]["extracted_data"] == []

    @pytest.mark.asyncio
    async def test_delete_analysis_then_document(self, db):
        doc_id = _create_doc(db)
        db.save_analysis_results(doc_id, ANALYSIS_DATA)

        await db.delete_analysis_data(doc_id)
        db.delete_document_record(doc_id)

        assert db.load_document_data(doc_id) is None
        assert db.get_analysis(doc_id) is None


class TestLocalStorageManager:
    def test_upload_writes_file_and_returns_served_url(self, storage):
        url = storage.upload_file(b"%PDF-1.4 fake", "abc.pdf")
        assert url.endswith("/api/v1/files/abc.pdf")
        assert (storage.upload_dir / "abc.pdf").read_bytes() == b"%PDF-1.4 fake"

    def test_upload_rejects_unexpected_extension(self, storage):
        with pytest.raises(ValueError):
            storage.upload_file(b"data", "evil.sh")

    @pytest.mark.asyncio
    async def test_delete_file(self, storage):
        storage.upload_file(b"data", "gone.pdf")
        await storage.delete_file("gone.pdf")
        assert not (storage.upload_dir / "gone.pdf").exists()

    @pytest.mark.asyncio
    async def test_delete_missing_file_is_silent(self, storage):
        await storage.delete_file("never-existed.pdf")
        await storage.delete_file_with_retry("never-existed.pdf")
