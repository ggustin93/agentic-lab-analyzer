# backend/tests/test_pipeline.py
import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

from services.document_processor import DocumentProcessor
from models.health_models import ExtractedHealthData, AnalyzedHealthData, ClinicalInsights, ExtractedHealthMarker

# Mark all tests in this file as asyncio
pytestmark = pytest.mark.asyncio

@pytest.fixture
def mock_supabase_client():
    """Fixture for a mocked Supabase client."""
    mock_client = MagicMock()
    mock_client.table.return_value.update.return_value.execute.return_value = None
    mock_client.table.return_value.insert.return_value.execute.return_value = None
    return mock_client

@pytest.fixture
def mock_agents():
    """Fixture for mocked agents."""
    # Mock for Agent 1: OCR
    mock_ocr_agent = AsyncMock()
    mock_ocr_agent.extract_text.return_value = "This is the extracted OCR text."

    # Mock for Agent 2: Extractor
    mock_extractor_agent = AsyncMock()
    mock_extractor_agent.extract_data.return_value = ExtractedHealthData(markers=[
        ExtractedHealthMarker(marker="Hemoglobin", value="14.5", unit="g/dL", range="13.5-17.5")
    ])
    mock_extractor_agent.analyze_data.return_value = AnalyzedHealthData(markers=[]) # Keep it simple

    # Mock for Agent 3: Insights
    mock_insight_agent = AsyncMock()
    mock_insight_agent.generate_insights.return_value = ClinicalInsights(
        summary="Patient shows normal hemoglobin levels.",
        recommendations=["Continue routine check-ups."]
    )
    
    return mock_ocr_agent, mock_extractor_agent, mock_insight_agent

@patch('services.document_processor.create_client')
async def test_document_processing_pipeline_success(mock_create_client, mock_agents, mock_supabase_client):
    """
    Tests the full document processing pipeline with mocked agents,
    ensuring each step is called in order and progress is updated correctly.
    """
    # Arrange
    mock_create_client.return_value = mock_supabase_client
    mock_ocr, mock_extractor, mock_insights = mock_agents

    # Patch the agents within the DocumentProcessor instance
    with patch('services.document_processor.MistralOCRService', return_value=mock_ocr), \
         patch('services.document_processor.LabDataExtractorAgent', return_value=mock_extractor), \
         patch('services.document_processor.ClinicalInsightAgent', return_value=mock_insights):

        processor = DocumentProcessor()
        # Mock the SSE progress updater method directly
        processor._update_progress = MagicMock()

        document_id = "test_doc_id"
        file_url = "http://fake.url/test.pdf"
        filename = "test.pdf"

        # Act
        await processor._process_document_async(document_id, file_url, filename)

        # Assert
        # 1. Verify OCR agent was called
        mock_ocr.extract_text.assert_awaited_once_with(file_url, ".pdf")
        
        # 2. Verify Extractor agent was called with OCR text
        mock_extractor.extract_data.assert_awaited_once_with("This is the extracted OCR text.")
        
        # 3. Verify Analyzer part of the extractor was called
        mock_extractor.analyze_data.assert_awaited_once()
        
        # 4. Verify Insight agent was called with analyzed data
        mock_insights.generate_insights.assert_awaited_once()

        # 5. Verify progress updates were called for each stage
        assert processor._update_progress.call_count == 6
        processor._update_progress.assert_any_call(document_id, 10, 'ocr_extraction')
        processor._update_progress.assert_any_call(document_id, 30, 'data_extraction')
        processor._update_progress.assert_any_call(document_id, 50, 'data_analysis')
        processor._update_progress.assert_any_call(document_id, 70, 'insight_generation')
        processor._update_progress.assert_any_call(document_id, 90, 'saving_results')
        processor._update_progress.assert_any_call(document_id, 100, 'complete')

        # 6. Verify data was saved to Supabase
        # Check that the final update call to set status to 'complete' happened
        mock_supabase_client.table.return_value.update.assert_any_call({'status': 'complete', 'completed_at': pytest.approx(0, abs=1), 'progress': 100})
        # Check that the results were inserted
        mock_supabase_client.table.return_value.insert.assert_called_once() 