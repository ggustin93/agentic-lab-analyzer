-- Baseline Schema Migration: Initial database structure
-- Date: 2025-01-01 (Retroactive documentation)
-- Description: Documents the baseline schema of the Agentic Lab Analyzer database

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ====================================
-- Documents Table
-- ====================================
CREATE TABLE IF NOT EXISTS documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    filename TEXT NOT NULL,
    upload_date TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT now(),
    status TEXT NOT NULL, -- 'processing', 'complete', 'error'
    user_id UUID,
    storage_path TEXT,
    public_url TEXT,
    error_message TEXT,
    processed_at TIMESTAMP WITH TIME ZONE,
    raw_text TEXT
);

-- ====================================
-- Analysis Results Table
-- ====================================
CREATE TABLE IF NOT EXISTS analysis_results (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    raw_text TEXT,
    structured_data JSONB,
    insights TEXT
);

-- ====================================
-- Health Markers Table
-- ====================================
CREATE TABLE IF NOT EXISTS health_markers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    analysis_id UUID NOT NULL REFERENCES analysis_results(id) ON DELETE CASCADE,
    marker_name TEXT,
    value TEXT, -- Using TEXT to handle various value formats
    unit TEXT,
    reference_range TEXT
);

-- ====================================
-- Indexes for Performance
-- ====================================
CREATE INDEX IF NOT EXISTS idx_documents_status ON documents(status);
CREATE INDEX IF NOT EXISTS idx_documents_upload_date ON documents(upload_date DESC);
CREATE INDEX IF NOT EXISTS idx_analysis_results_document_id ON analysis_results(document_id);
CREATE INDEX IF NOT EXISTS idx_health_markers_analysis_id ON health_markers(analysis_id);

-- ====================================
-- Add Unique Constraint for Analysis Results
-- ====================================
-- Ensure one analysis result per document
CREATE UNIQUE INDEX IF NOT EXISTS idx_analysis_results_document_unique 
ON analysis_results(document_id);

-- ====================================
-- Comments for Documentation
-- ====================================
COMMENT ON TABLE documents IS 'Stores uploaded health documents and their processing status';
COMMENT ON TABLE analysis_results IS 'Stores AI analysis results for each document';
COMMENT ON TABLE health_markers IS 'Stores individual health markers extracted from analysis';

COMMENT ON COLUMN documents.status IS 'Processing status: processing, complete, error';
COMMENT ON COLUMN documents.raw_text IS 'OCR extracted text from the document';
COMMENT ON COLUMN analysis_results.structured_data IS 'JSON structure containing extracted health data';
COMMENT ON COLUMN health_markers.value IS 'Marker value as text to handle various formats'; 