"""
API-level tests for server-side upload validation and bounded SSE streams
(backlog 001, 002, 006). Everything runs against mocks: the processor is
substituted through FastAPI's dependency_overrides — no patching of module
globals needed, thanks to the lazy composition root in main.py.
"""

import io
from unittest.mock import patch, MagicMock, AsyncMock

import pytest
from fastapi.testclient import TestClient

from main import app, get_document_processor, GENERIC_ERROR_MESSAGES

client = TestClient(app)

# A minimal but genuine PDF header so magic-bytes detection sees a real PDF
PDF_BYTES = b"%PDF-1.4\n1 0 obj<</Type/Catalog>>endobj\ntrailer<<>>\n%%EOF"


@pytest.fixture
def processor():
    """Fake DocumentProcessor injected in place of the real composition root."""
    fake = MagicMock()
    fake.process_document = AsyncMock(return_value="doc-123")
    app.dependency_overrides[get_document_processor] = lambda: fake
    yield fake
    app.dependency_overrides.clear()


def _upload(content: bytes, filename: str = "report.pdf"):
    return client.post(
        "/api/v1/documents/upload",
        files={"file": (filename, io.BytesIO(content), "application/pdf")},
    )


class TestUploadValidation:

    def test_oversized_file_is_rejected_with_413(self, processor):
        """An oversized body is rejected and nothing reaches the processor."""
        with patch('main.settings.MAX_FILE_SIZE', 1024):
            response = _upload(b"x" * 2048)
        assert response.status_code == 413
        processor.process_document.assert_not_called()

    def test_wrong_content_is_rejected_with_415_despite_pdf_name(self, processor):
        """Type is judged on magic bytes, not on the filename."""
        response = _upload(b"just some text pretending", filename="fake.pdf")
        assert response.status_code == 415
        processor.process_document.assert_not_called()

    def test_empty_file_is_rejected(self, processor):
        response = _upload(b"")
        assert response.status_code == 415

    def test_valid_pdf_is_accepted_with_202(self, processor):
        response = _upload(PDF_BYTES)
        assert response.status_code == 202
        assert response.json()["document_id"] == "doc-123"

    def test_processing_failure_returns_generic_message(self, processor):
        """Internal exception text never reaches the client (backlog 006)."""
        processor.process_document = AsyncMock(
            side_effect=Exception("supabase host db.internal:5432 exploded")
        )
        response = _upload(PDF_BYTES)
        assert response.status_code == 500
        assert response.json()["detail"] == GENERIC_ERROR_MESSAGES["upload"]
        assert "db.internal" not in response.text


class TestSSEStream:

    def test_unknown_document_returns_404_immediately(self, processor):
        """No stream — and no polling loop — for an id that does not exist."""
        processor.get_analysis = MagicMock(return_value=None)
        response = client.get("/api/v1/documents/does-not-exist/stream")
        assert response.status_code == 404

    def test_terminal_document_streams_one_event_and_closes(self, processor):
        doc = {"id": "doc-1", "status": "complete"}
        processor.get_analysis = MagicMock(return_value=doc)
        with client.stream("GET", "/api/v1/documents/doc-1/stream") as response:
            assert response.status_code == 200
            body = b"".join(response.iter_raw())
        assert b'"complete"' in body
