-- SQLite schema for local mode (ADR-008).
-- Mirrors supabase/migrations/ with SQLite-compatible types: UUIDs and
-- timestamps are generated in Python and stored as TEXT; structured_data is
-- JSON-serialized TEXT.

CREATE TABLE IF NOT EXISTS documents (
    id TEXT PRIMARY KEY,
    filename TEXT NOT NULL,
    upload_date TEXT NOT NULL,
    status TEXT NOT NULL, -- 'processing', 'complete', 'error'
    user_id TEXT,
    storage_path TEXT,
    public_url TEXT,
    error_message TEXT,
    processed_at TEXT,
    raw_text TEXT,
    progress INTEGER DEFAULT 0,
    processing_stage TEXT DEFAULT NULL
);

CREATE TABLE IF NOT EXISTS analysis_results (
    id TEXT PRIMARY KEY,
    document_id TEXT NOT NULL REFERENCES documents(id) ON DELETE CASCADE,
    raw_text TEXT,
    structured_data TEXT, -- JSON
    insights TEXT
);

CREATE TABLE IF NOT EXISTS health_markers (
    id TEXT PRIMARY KEY,
    analysis_id TEXT NOT NULL REFERENCES analysis_results(id) ON DELETE CASCADE,
    marker_name TEXT,
    value TEXT,
    unit TEXT,
    reference_range TEXT
);

CREATE INDEX IF NOT EXISTS idx_documents_status ON documents(status);
CREATE INDEX IF NOT EXISTS idx_documents_upload_date ON documents(upload_date DESC);
CREATE INDEX IF NOT EXISTS idx_analysis_results_document_id ON analysis_results(document_id);
CREATE INDEX IF NOT EXISTS idx_health_markers_analysis_id ON health_markers(analysis_id);
CREATE UNIQUE INDEX IF NOT EXISTS idx_analysis_results_document_unique ON analysis_results(document_id);
