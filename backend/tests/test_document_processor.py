import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from services.document_processor import DocumentProcessor
from models.health_models import HealthInsights, HealthDataExtraction, HealthMarker

@pytest.fixture
def mock_ocr_agent():
    mock = AsyncMock()
    mock.extract_text.return_value = "This is the extracted text."
    return mock

@pytest.fixture
def mock_insight_agent():
    mock = AsyncMock()
    mock.analyze_text.return_value = HealthInsights(
        data=HealthDataExtraction(
            markers=[
                HealthMarker(marker="Hemoglobin", value="15.0", unit="g/dL", reference_range="13.5-17.5")
            ],
            document_type="Blood Test",
            test_date="2023-01-01T00:00:00"
        ),
        summary="This is a summary.",
        key_findings=["Finding 1"],
        recommendations=["Recommendation 1"],
        disclaimer="This is a disclaimer."
    )
    return mock

@pytest.fixture
def document_processor(mock_ocr_agent, mock_insight_agent):
    with patch('services.document_processor.MistralOCRService', return_value=mock_ocr_agent), \
         patch('services.document_processor.ChutesAILabAgent', return_value=mock_insight_agent):
        processor = DocumentProcessor()
        # Mock storage methods to prevent file system access
        processor._save_document_data = AsyncMock()
        processor._load_document_data = AsyncMock(return_value={
            "id": "test_doc_id",
            "filename": "test.pdf",
            "uploaded_at": "2023-01-01T00:00:00",
            "status": "processing",
            "file_path": "/fake/path/test.pdf"
        })
        return processor

@pytest.mark.asyncio
async def test_process_document_async_success(document_processor, mock_ocr_agent, mock_insight_agent):
    """
    Tests the successful processing of a document through the async pipeline.
    """
    document_id = "test_doc_id"
    file_path = "/fake/path/test.pdf"
    filename = "test.pdf"

    await document_processor._process_document_async(document_id, file_path, filename)

    # Verify that the agents were called correctly
    mock_ocr_agent.extract_text.assert_called_once_with(file_path, "pdf")
    mock_insight_agent.analyze_text.assert_called_once_with("This is the extracted text.")

    # Verify that the data was saved with the correct status and content
    document_processor._save_document_data.assert_called_once()
    saved_data = document_processor._save_document_data.call_args[0][1]
    
    assert saved_data['status'] == 'complete'
    assert saved_data['raw_text'] == "This is the extracted text."
    assert len(saved_data['extracted_data']) == 1
    assert saved_data['extracted_data'][0]['marker'] == 'Hemoglobin'
    assert "Analysis Report" in saved_data['ai_insights']
    assert "Disclaimer" in saved_data['ai_insights']

@pytest.mark.asyncio
async def test_process_document_async_ocr_failure(document_processor, mock_ocr_agent):
    """
    Tests how the processor handles a failure when the OCR process yields no text.
    """
    mock_ocr_agent.extract_text.return_value = ""  # Simulate OCR returning no text

    document_id = "test_doc_id"
    file_path = "/fake/path/test.pdf"
    filename = "test.pdf"

    await document_processor._process_document_async(document_id, file_path, filename)
    
    document_processor.ocr_agent.extract_text.assert_called_once_with(file_path, "pdf")
    document_processor.insight_agent.analyze_text.assert_not_called()

    saved_data = document_processor._save_document_data.call_args[0][1]
    assert saved_data['status'] == 'error'
    assert "OCR process yielded no text" in saved_data['error_message']

@pytest.mark.asyncio
async def test_process_document_async_insight_agent_failure(document_processor, mock_insight_agent):
    """
    Tests how the processor handles a failure during the insight generation step.
    """
    mock_insight_agent.analyze_text.side_effect = Exception("AI agent failed")

    document_id = "test_doc_id"
    file_path = "/fake/path/test.pdf"
    filename = "test.pdf"

    await document_processor._process_document_async(document_id, file_path, filename)

    document_processor.insight_agent.analyze_text.assert_called_once()
    
    saved_data = document_processor._save_document_data.call_args[0][1]
    assert saved_data['status'] == 'error'
    assert "AI agent failed" in saved_data['error_message'] 