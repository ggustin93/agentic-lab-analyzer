import pytest
from unittest.mock import patch, MagicMock, AsyncMock

from services.document_processor import DocumentProcessor
from services.processing_pipeline import ProcessingPipeline


@pytest.fixture
def mock_database_manager():
    """Fake DocumentRepository (ADR-008 port)."""
    db = MagicMock()
    db.delete_analysis_data = AsyncMock()
    db.list_documents = AsyncMock(return_value=[])
    return db


@pytest.fixture
def mock_storage_manager():
    """Fake FileStorage (ADR-008 port)."""
    storage = MagicMock()
    storage.upload_file.return_value = "http://fake.url/test.pdf"
    storage.delete_file = AsyncMock()
    storage.delete_file_with_retry = AsyncMock()
    return storage


@pytest.fixture
def mock_processing_pipeline():
    """Mock processing pipeline with async methods."""
    mock_pipeline = MagicMock(spec=ProcessingPipeline)
    mock_pipeline.process_document_async = AsyncMock()
    mock_pipeline.retry_processing = AsyncMock(return_value=True)
    return mock_pipeline


@pytest.fixture
def document_processor(mock_database_manager, mock_storage_manager, mock_processing_pipeline):
    """DocumentProcessor with fake adapters injected through the constructor."""
    processor = DocumentProcessor(mock_database_manager, mock_storage_manager)
    processor.processing_pipeline = mock_processing_pipeline
    return processor


@pytest.mark.asyncio
async def test_process_document_success(document_processor, mock_database_manager, mock_processing_pipeline):
    """Test successful document processing."""
    document_id = await document_processor.process_document(b"test file content", "test.pdf")

    assert document_id is not None
    assert len(document_id) == 36  # UUID length
    mock_database_manager.create_document_record.assert_called_once()
    mock_processing_pipeline.process_document_async.assert_called_once()


@pytest.mark.asyncio
async def test_delete_document_success(document_processor, mock_database_manager, mock_storage_manager):
    """Test successful document deletion."""
    mock_database_manager.load_document_data.return_value = {"id": "test_doc", "storage_path": "test.pdf"}

    result = await document_processor.delete_document("test_doc")

    assert result is True
    mock_database_manager.delete_analysis_data.assert_called_once_with("test_doc")
    mock_storage_manager.delete_file_with_retry.assert_called_once_with("test.pdf")
    mock_database_manager.delete_document_record.assert_called_once_with("test_doc")


@pytest.mark.asyncio
async def test_delete_document_not_found(document_processor, mock_database_manager):
    """Test deletion of non-existent document."""
    mock_database_manager.load_document_data.return_value = None

    result = await document_processor.delete_document("non_existent")

    assert result is False


@pytest.mark.asyncio
async def test_retry_document_processing(document_processor, mock_processing_pipeline):
    """Test document processing retry."""
    result = await document_processor.retry_document_processing("test_doc")

    assert result is True
    mock_processing_pipeline.retry_processing.assert_called_once_with("test_doc")


@pytest.mark.asyncio
async def test_list_documents(document_processor, mock_database_manager):
    """Test listing documents."""
    mock_database_manager.list_documents.return_value = [
        {"document_id": "doc1", "filename": "test1.pdf"},
        {"document_id": "doc2", "filename": "test2.pdf"},
    ]

    result = await document_processor.list_documents()

    assert len(result) == 2
    assert result[0]["document_id"] == "doc1"


def test_get_analysis(document_processor, mock_database_manager):
    """Test getting document analysis."""
    mock_analysis = {"document_id": "test_doc", "status": "complete"}
    mock_database_manager.get_analysis.return_value = mock_analysis

    result = document_processor.get_analysis("test_doc")

    assert result == mock_analysis
    mock_database_manager.get_analysis.assert_called_once_with("test_doc")


@pytest.mark.asyncio
async def test_delete_with_retry_logic(document_processor, mock_database_manager):
    """Test delete document with retry logic."""
    mock_database_manager.load_document_data.return_value = {"id": "test_doc", "storage_path": "test.pdf"}
    # Fail twice, then succeed
    mock_database_manager.delete_document_record.side_effect = [
        Exception("DB Error"), Exception("DB Error"), None,
    ]

    with patch('asyncio.sleep'):
        result = await document_processor.delete_document("test_doc")

    assert result is True
    assert mock_database_manager.delete_document_record.call_count == 3


@pytest.mark.asyncio
async def test_delete_max_retries_exceeded(document_processor, mock_database_manager):
    """Test delete document when max retries exceeded."""
    mock_database_manager.load_document_data.return_value = {"id": "test_doc", "storage_path": "test.pdf"}
    mock_database_manager.delete_document_record.side_effect = Exception("Permanent DB Error")

    with patch('asyncio.sleep'):
        result = await document_processor.delete_document("test_doc")

    assert result is False
    assert mock_database_manager.delete_document_record.call_count == 3


def test_smoke_test(mock_database_manager, mock_storage_manager):
    """Simple test to verify basic wiring."""
    processor = DocumentProcessor(mock_database_manager, mock_storage_manager)

    assert processor is not None
    assert processor.storage_manager is mock_storage_manager
    assert processor.database_manager is mock_database_manager
    assert processor.processing_pipeline is not None
