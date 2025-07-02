-- Migration: Add progress tracking columns to documents table
-- Date: 2025-01-02
-- Description: Adds progress and processing_stage columns to enable real-time progress tracking during document analysis

-- Add progress tracking columns to documents table
ALTER TABLE documents 
ADD COLUMN progress INTEGER DEFAULT 0,
ADD COLUMN processing_stage TEXT DEFAULT NULL;

-- Add comment for documentation
COMMENT ON COLUMN documents.progress IS 'Processing progress percentage (0-100)';
COMMENT ON COLUMN documents.processing_stage IS 'Current processing stage: ocr_extraction, ai_analysis, saving_results, complete';

-- Create index for querying by processing status
CREATE INDEX IF NOT EXISTS idx_documents_processing 
ON documents(status, processing_stage) 
WHERE status = 'processing'; 