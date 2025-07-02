-- Rollback Migration: Remove progress tracking columns from documents table
-- Date: 2025-01-02
-- Description: Removes progress and processing_stage columns added in 20250102_001_add_progress_tracking_columns.sql

-- Drop the index first
DROP INDEX IF EXISTS idx_documents_processing;

-- Remove the progress tracking columns
ALTER TABLE documents 
DROP COLUMN IF EXISTS progress,
DROP COLUMN IF EXISTS processing_stage; 