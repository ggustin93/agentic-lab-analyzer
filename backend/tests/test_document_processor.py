import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime
import logging
from supabase import Client

from services.document_processor import DocumentProcessor
from models.health_models import HealthInsights, HealthMarker, HealthDataExtraction

@pytest.fixture
def mock_ocr_agent():
    """Mock OCR agent that returns predefined text."""
    mock = AsyncMock()
    mock.extract_text_from_pdf.return_value = "This is the extracted text."
    mock.extract_text_from_image.return_value = "This is the extracted text."
    return mock

@pytest.fixture
def mock_insight_agent():
    """Mock insight agent that returns a predefined HealthInsights object."""
    mock = AsyncMock()
    mock.analyze_text.return_value = HealthInsights(
        data=HealthDataExtraction(
            markers=[HealthMarker(marker="Hemoglobin", value="14", unit="g/dL", reference_range="13-17")],
            document_type="Blood Test",
            test_date=datetime.now()
        ),
        summary="Test summary",
        key_findings=["Finding 1"],
        recommendations=["Recommendation 1"],
        disclaimer="Test disclaimer"
    )
    return mock

@pytest.fixture
def document_processor(mock_ocr_agent, mock_insight_agent):
    """Fixture for DocumentProcessor with mocked dependencies."""
    with patch('services.document_processor.create_client') as mock_create_client:
        mock_supabase_client = MagicMock(spec=Client)
        
        # Mock the chained calls
        mock_table_instance = MagicMock()
        mock_supabase_client.table.return_value = mock_table_instance

        # Mock storage client
        mock_storage_client = MagicMock()
        mock_supabase_client.storage.from_.return_value = mock_storage_client
        mock_storage_client.upload.return_value = None
        mock_storage_client.get_public_url.return_value = "http://fake.url/test.pdf"

        # Mock for _load_document_data (which happens first)
        # It can be called multiple times, so we need different return values if necessary
        mock_select_builder = MagicMock()
        mock_table_instance.select.return_value = mock_select_builder
        mock_select_builder.eq.return_value = mock_select_builder
        mock_select_builder.maybe_single.return_value = mock_select_builder
        
        # Mock return value for the initial load
        load_return_mock = AsyncMock()
        load_return_mock.return_value = MagicMock(data={"id": "test_doc_id", "status": "processing"})
        mock_select_builder.execute = load_return_mock
        
        # Mock for upsert in _save_document_data
        mock_upsert_builder = MagicMock()
        mock_table_instance.upsert.return_value = mock_upsert_builder
        mock_upsert_builder.execute = AsyncMock(return_value=MagicMock(data=[{'id': 'mock_analysis_id'}]))
        
        # Mock for update in _save_document_data
        mock_update_builder = MagicMock()
        mock_table_instance.update.return_value = mock_update_builder
        mock_update_builder.eq.return_value = mock_update_builder
        mock_update_builder.execute = AsyncMock()

        # Mock for insert in _save_document_data
        mock_insert_builder = MagicMock()
        mock_table_instance.insert.return_value = mock_insert_builder
        mock_insert_builder.execute = AsyncMock()

        # Mock for delete in _save_document_data
        mock_delete_builder = MagicMock()
        mock_table_instance.delete.return_value = mock_delete_builder
        mock_delete_builder.eq.return_value = mock_delete_builder
        mock_delete_builder.execute = AsyncMock()
        
        mock_create_client.return_value = mock_supabase_client
        
        processor = DocumentProcessor()
        processor.ocr_agent = mock_ocr_agent
        processor.insight_agent = mock_insight_agent
        processor.supabase = mock_supabase_client
        return processor

@pytest.mark.asyncio
async def test_process_document_async_success(document_processor, mock_ocr_agent, mock_insight_agent):
    """
    Tests the successful processing of a document through the async pipeline.
    """
    document_id = "test_doc_id"
    file_url = "http://fake.url/test.pdf"
    filename = "test.pdf"

    # Add logging to inspect the mock
    logging.info(f"MOCK IN TEST (before call): {document_processor.supabase}")

    await document_processor._process_document_async(document_id, file_url, filename)

    # 1. Verify agents were called correctly
    mock_ocr_agent.extract_text_from_pdf.assert_called_once_with(file_url)
    mock_insight_agent.analyze_text.assert_called_once_with("This is the extracted text.")

    # 2. Verify Supabase update for the main document
    update_call = document_processor.supabase.table.return_value.update.call_args
    assert update_call is not None
    update_payload = update_call.args[0]
    assert update_payload['status'] == 'complete'
    assert 'raw_text' in update_payload

    # 3. Verify Supabase upsert for analysis_results
    upsert_call = document_processor.supabase.table.return_value.upsert.call_args
    assert upsert_call is not None
    upsert_payload = upsert_call.args[0]
    assert upsert_payload['document_id'] == document_id
    assert 'Analysis Report' in upsert_payload['insights']

    # 4. Verify Supabase insert for health_markers
    insert_call = document_processor.supabase.table.return_value.insert.call_args
    assert insert_call is not None
    insert_payload = insert_call.args[0]
    assert len(insert_payload) == 1
    assert insert_payload[0]['marker_name'] == 'Hemoglobin'


@pytest.mark.asyncio
async def test_process_document_async_ocr_failure(document_processor, mock_ocr_agent):
    """
    Tests how the processor handles a failure when the OCR process yields no text.
    """
    mock_ocr_agent.extract_text_from_pdf.return_value = ""

    document_id = "test_doc_id"
    file_url = "http://fake.url/test.pdf"
    filename = "test.pdf"

    await document_processor._process_document_async(document_id, file_url, filename)

    mock_ocr_agent.extract_text_from_pdf.assert_called_once_with(file_url)
    document_processor.insight_agent.analyze_text.assert_not_called()

    update_call = document_processor.supabase.table.return_value.update.call_args
    assert update_call is not None
    update_payload = update_call.args[0]
    assert update_payload['status'] == 'error'
    assert "OCR process yielded no text" in update_payload['error_message']


@pytest.mark.asyncio
async def test_process_document_async_insight_agent_failure(document_processor, mock_ocr_agent, mock_insight_agent):
    """
    Tests how the processor handles a failure during the insight generation step.
    """
    mock_insight_agent.analyze_text.side_effect = Exception("AI agent failed")

    document_id = "test_doc_id"
    file_url = "http://fake.url/test.pdf"
    filename = "test.pdf"

    await document_processor._process_document_async(document_id, file_url, filename)

    mock_ocr_agent.extract_text_from_pdf.assert_called_once_with(file_url)
    mock_insight_agent.analyze_text.assert_called_once()
    
    update_call = document_processor.supabase.table.return_value.update.call_args
    assert update_call is not None
    update_payload = update_call.args[0]
    assert update_payload['status'] == 'error'
    assert "AI agent failed" in update_payload['error_message']

@pytest.mark.asyncio
async def test_smoke_test():
    """A very simple test to see if the event loop and fixtures are working."""
    with patch('services.document_processor.create_client') as mock_create_client:
        
        mock_supabase_client = MagicMock()
        mock_create_client.return_value = mock_supabase_client
        
        processor = DocumentProcessor()
        processor.supabase = mock_supabase_client
        
        # A minimal assertion
        assert processor is not None
        assert processor.supabase is not None 