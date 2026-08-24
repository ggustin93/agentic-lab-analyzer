import pytest
from unittest.mock import patch, MagicMock, AsyncMock
from datetime import datetime
import logging
from supabase import Client

from services.document_processor import DocumentProcessor
from services.storage_manager import StorageManager
from services.database_manager import DatabaseManager
from services.processing_pipeline import ProcessingPipeline
from models.health_models import HealthInsights, HealthMarker, HealthDataExtraction

@pytest.fixture
def mock_supabase_client():
    """Mock Supabase client with all necessary operations."""
    mock_client = MagicMock(spec=Client)
    
    # Mock storage operations
    mock_storage = MagicMock()
    mock_client.storage.from_.return_value = mock_storage
    mock_storage.upload.return_value = None
    mock_storage.get_public_url.return_value = "http://fake.url/test.pdf"
    mock_storage.remove.return_value = None
    
    # Mock table operations
    mock_table = MagicMock()
    mock_client.table.return_value = mock_table
    
    # Mock select chain
    mock_select = MagicMock()
    mock_table.select.return_value = mock_select
    mock_select.eq.return_value = mock_select
    mock_select.maybe_single.return_value = mock_select
    mock_select.order.return_value = mock_select
    mock_select.execute.return_value = MagicMock(data={"id": "test_doc", "status": "processing"})
    
    # Mock other operations
    mock_table.insert.return_value = MagicMock(execute=MagicMock())
    mock_table.update.return_value = MagicMock(eq=MagicMock(return_value=MagicMock(execute=MagicMock())))
    mock_table.delete.return_value = MagicMock(eq=MagicMock(return_value=MagicMock(execute=MagicMock())))
    mock_table.upsert.return_value = MagicMock(execute=MagicMock(return_value=MagicMock(data=[{'id': 'analysis_id'}])))
    
    return mock_client

@pytest.fixture
def mock_processing_pipeline():
    """Mock processing pipeline with async methods."""
    mock_pipeline = MagicMock(spec=ProcessingPipeline)
    mock_pipeline.process_document_async = AsyncMock()
    mock_pipeline.retry_processing = AsyncMock(return_value=True)
    return mock_pipeline

@pytest.fixture
def document_processor(mock_supabase_client, mock_processing_pipeline):
    """Create DocumentProcessor with mocked dependencies."""
    with patch('services.document_processor.create_client') as mock_create_client:
        mock_create_client.return_value = mock_supabase_client
        
        processor = DocumentProcessor()
        processor.processing_pipeline = mock_processing_pipeline
        
        return processor

@pytest.mark.asyncio
async def test_process_document_success(document_processor, mock_processing_pipeline):
    """Test successful document processing."""
    # Test data
    file_content = b"test file content"
    filename = "test.pdf"
    
    # Execute
    document_id = await document_processor.process_document(file_content, filename)
    
    # Assertions
    assert document_id is not None
    assert len(document_id) == 36  # UUID length
    
    # Verify pipeline was called
    mock_processing_pipeline.process_document_async.assert_called_once()

@pytest.mark.asyncio
async def test_delete_document_success():
    """Test successful document deletion."""
    with patch('services.document_processor.create_client') as mock_create_client:
        # Setup mock
        mock_supabase_client = MagicMock(spec=Client)
        mock_create_client.return_value = mock_supabase_client
        
        # Mock document data
        mock_document_data = {"id": "test_doc", "storage_path": "test.pdf"}
        
        processor = DocumentProcessor()
        
        # Mock the database manager methods directly
        processor.database_manager.load_document_data = MagicMock(return_value=mock_document_data)
        processor.database_manager.delete_analysis_data = AsyncMock()
        processor.database_manager.delete_document_record = MagicMock()
        processor.storage_manager.delete_file_with_retry = AsyncMock()
        
        # Execute
        result = await processor.delete_document("test_doc")
        
        # Assertions
        assert result is True
        processor.database_manager.delete_analysis_data.assert_called_once_with("test_doc")
        processor.storage_manager.delete_file_with_retry.assert_called_once_with("test.pdf")
        processor.database_manager.delete_document_record.assert_called_once_with("test_doc")

@pytest.mark.asyncio
async def test_delete_document_not_found():
    """Test deletion of non-existent document."""
    with patch('services.document_processor.create_client') as mock_create_client:
        mock_supabase_client = MagicMock(spec=Client)
        mock_create_client.return_value = mock_supabase_client
        
        processor = DocumentProcessor()
        processor.database_manager.load_document_data = MagicMock(return_value=None)
        
        # Execute
        result = await processor.delete_document("non_existent")
        
        # Assertions
        assert result is False

@pytest.mark.asyncio
async def test_retry_document_processing(document_processor, mock_processing_pipeline):
    """Test document processing retry."""
    # Execute
    result = await document_processor.retry_document_processing("test_doc")
    
    # Assertions
    assert result is True
    mock_processing_pipeline.retry_processing.assert_called_once_with("test_doc")

@pytest.mark.asyncio
async def test_list_documents(document_processor):
    """Test listing documents."""
    # Mock the database manager
    document_processor.database_manager.list_documents = AsyncMock(return_value=[
        {"document_id": "doc1", "filename": "test1.pdf"},
        {"document_id": "doc2", "filename": "test2.pdf"}
    ])
    
    # Execute
    result = await document_processor.list_documents()
    
    # Assertions
    assert len(result) == 2
    assert result[0]["document_id"] == "doc1"

def test_get_analysis(document_processor):
    """Test getting document analysis."""
    # Mock the database manager
    mock_analysis = {"document_id": "test_doc", "status": "complete"}
    document_processor.database_manager.get_analysis = MagicMock(return_value=mock_analysis)
    
    # Execute
    result = document_processor.get_analysis("test_doc")
    
    # Assertions
    assert result == mock_analysis
    document_processor.database_manager.get_analysis.assert_called_once_with("test_doc")

@pytest.mark.asyncio
async def test_delete_with_retry_logic():
    """Test delete document with retry logic."""
    with patch('services.document_processor.create_client') as mock_create_client:
        mock_supabase_client = MagicMock(spec=Client)
        mock_create_client.return_value = mock_supabase_client
        
        processor = DocumentProcessor()
        mock_document_data = {"id": "test_doc", "storage_path": "test.pdf"}
        
        # Mock methods to fail first, then succeed
        processor.database_manager.load_document_data = MagicMock(return_value=mock_document_data)
        processor.database_manager.delete_analysis_data = AsyncMock()
        processor.storage_manager.delete_file_with_retry = AsyncMock()
        
        # Make document record deletion fail twice, then succeed
        processor.database_manager.delete_document_record = MagicMock(
            side_effect=[Exception("DB Error"), Exception("DB Error"), None]
        )
        
        # Patch sleep to speed up test
        with patch('asyncio.sleep'):
            result = await processor.delete_document("test_doc")
        
        # Should succeed on third attempt
        assert result is True
        assert processor.database_manager.delete_document_record.call_count == 3

@pytest.mark.asyncio  
async def test_delete_max_retries_exceeded():
    """Test delete document when max retries exceeded."""
    with patch('services.document_processor.create_client') as mock_create_client:
        mock_supabase_client = MagicMock(spec=Client)
        mock_create_client.return_value = mock_supabase_client
        
        processor = DocumentProcessor()
        mock_document_data = {"id": "test_doc", "storage_path": "test.pdf"}
        
        # Mock methods
        processor.database_manager.load_document_data = MagicMock(return_value=mock_document_data)
        processor.database_manager.delete_analysis_data = AsyncMock()
        processor.storage_manager.delete_file_with_retry = AsyncMock()
        
        # Make document record deletion always fail
        processor.database_manager.delete_document_record = MagicMock(
            side_effect=Exception("Permanent DB Error")
        )
        
        # Patch sleep to speed up test
        with patch('asyncio.sleep'):
            result = await processor.delete_document("test_doc")
        
        # Should fail after max retries
        assert result is False
        assert processor.database_manager.delete_document_record.call_count == 3

def test_smoke_test():
    """Simple test to verify basic functionality."""
    with patch('services.document_processor.create_client') as mock_create_client:
        mock_supabase_client = MagicMock()
        mock_create_client.return_value = mock_supabase_client
        
        processor = DocumentProcessor()
        
        # Basic assertion
        assert processor is not None
        assert hasattr(processor, 'storage_manager')
        assert hasattr(processor, 'database_manager')
        assert hasattr(processor, 'processing_pipeline')