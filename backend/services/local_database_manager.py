"""
Local Database Manager (ADR-008)

SQLite implementation of the DocumentRepository port. Same public surface as
DatabaseManager (the Supabase adapter), stdlib sqlite3 only — rows are
exchanged as plain dicts and reshaped so document_presenter receives the same
structure the Supabase join produces.
"""

import json
import logging
import sqlite3
import threading
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, List, Optional

from models.health_models import HealthInsights
from services.document_presenter import format_insights_as_markdown, format_document_for_frontend

logger = logging.getLogger(__name__)

_SCHEMA_PATH = Path(__file__).parent / "schema.sql"

_STAGE_PROGRESS = {
    "ocr_extraction": 10,
    "ai_analysis": 50,
    "saving_results": 90,
    "complete": 100,
}


class LocalDatabaseManager:
    """DocumentRepository adapter backed by a local SQLite file."""

    def __init__(self, db_path: str):
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        # ponytail: single shared conn + lock; connection-per-request if it ever contends
        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._lock = threading.Lock()
        self._conn.execute("PRAGMA journal_mode=WAL")
        self._conn.execute("PRAGMA foreign_keys=ON")
        self._conn.executescript(_SCHEMA_PATH.read_text())
        self._conn.commit()
        logger.info(f"Local database initialized at {db_path}")

    def _execute(self, sql: str, params: tuple = ()) -> None:
        with self._lock:
            self._conn.execute(sql, params)
            self._conn.commit()

    def _fetchone(self, sql: str, params: tuple = ()) -> Optional[Dict]:
        with self._lock:
            row = self._conn.execute(sql, params).fetchone()
        return dict(row) if row else None

    def _fetchall(self, sql: str, params: tuple = ()) -> List[Dict]:
        with self._lock:
            rows = self._conn.execute(sql, params).fetchall()
        return [dict(row) for row in rows]

    @staticmethod
    def _with_analysis(row: Dict) -> Dict:
        """Reshape a joined row to the structure the presenter expects."""
        structured = row.pop("ar_structured_data", None)
        insights = row.pop("ar_insights", None)
        if structured is not None or insights is not None:
            row["analysis_results"] = [{
                "structured_data": json.loads(structured) if structured else None,
                "insights": insights,
            }]
        else:
            row["analysis_results"] = []
        return row

    _JOIN_SELECT = """
        SELECT d.*, ar.structured_data AS ar_structured_data, ar.insights AS ar_insights
        FROM documents d
        LEFT JOIN analysis_results ar ON ar.document_id = d.id
    """

    def create_document_record(self, document_id: str, filename: str, storage_path: str, public_url: str) -> None:
        try:
            self._execute(
                "INSERT INTO documents (id, filename, status, storage_path, public_url, upload_date) "
                "VALUES (?, ?, 'processing', ?, ?, ?)",
                (document_id, filename, storage_path, public_url, datetime.now(timezone.utc).isoformat()),
            )
            logger.info(f"Created initial record for document {document_id}")
        except Exception as e:
            logger.error(f"Error creating document record {document_id}: {e}", exc_info=True)
            raise

    def update_processing_stage(self, document_id: str, stage: str, extra_data: Optional[Dict] = None) -> None:
        try:
            update_data = {"processing_stage": stage, "progress": _STAGE_PROGRESS.get(stage, 0)}
            if extra_data:
                update_data.update(extra_data)
            assignments = ", ".join(f"{column} = ?" for column in update_data)
            self._execute(
                f"UPDATE documents SET {assignments} WHERE id = ?",
                (*update_data.values(), document_id),
            )
            logger.info(f"Updated processing stage for {document_id}: {stage}")
        except Exception as e:
            logger.error(f"Error updating processing stage for {document_id}: {e}", exc_info=True)
            raise

    def mark_document_error(self, document_id: str, error_message: str) -> None:
        try:
            self._execute(
                "UPDATE documents SET status = 'error', error_message = ? WHERE id = ?",
                (str(error_message), document_id),
            )
            logger.info(f"Marked document {document_id} as error: {error_message}")
        except Exception as e:
            logger.error(f"Error marking document {document_id} as failed: {e}", exc_info=True)
            raise

    def update_document_raw_text(self, document_id: str, raw_text: str) -> None:
        try:
            self._execute("UPDATE documents SET raw_text = ? WHERE id = ?", (raw_text, document_id))
            logger.info(f"Updated raw_text for document {document_id}")
        except Exception as e:
            # Not re-raised: matches the Supabase adapter — this is not a critical failure
            logger.error(f"Error updating raw_text for {document_id}: {e}", exc_info=True)

    def update_document_table(self, document_id: str, data: Dict) -> None:
        processed_at = datetime.now(timezone.utc).isoformat() if data["status"] == "complete" else None
        self._execute(
            "UPDATE documents SET status = ?, error_message = ?, progress = ?, processing_stage = ?, "
            "processed_at = COALESCE(?, processed_at) WHERE id = ?",
            (
                data["status"],
                data.get("error_message"),
                data.get("progress"),
                data.get("processing_stage"),
                processed_at,
                document_id,
            ),
        )
        logger.info(f"Updated document table for {document_id}")

    def save_analysis_results(self, document_id: str, analysis_data: Dict) -> None:
        doc = self._fetchone("SELECT raw_text FROM documents WHERE id = ?", (document_id,))
        raw_text = doc.get("raw_text") if doc else None
        insights = format_insights_as_markdown(HealthInsights(**analysis_data))

        with self._lock:
            row = self._conn.execute(
                "INSERT INTO analysis_results (id, document_id, raw_text, structured_data, insights) "
                "VALUES (?, ?, ?, ?, ?) "
                "ON CONFLICT(document_id) DO UPDATE SET raw_text = excluded.raw_text, "
                "structured_data = excluded.structured_data, insights = excluded.insights "
                "RETURNING id",
                (str(uuid.uuid4()), document_id, raw_text, json.dumps(analysis_data), insights),
            ).fetchone()
            self._conn.commit()
        analysis_id = row["id"]

        markers = analysis_data.get("data", {}).get("markers", [])
        if markers:
            self._save_health_markers(analysis_id, markers)

    def _save_health_markers(self, analysis_id: str, markers: List[Dict]) -> None:
        with self._lock:
            self._conn.execute("DELETE FROM health_markers WHERE analysis_id = ?", (analysis_id,))
            self._conn.executemany(
                "INSERT INTO health_markers (id, analysis_id, marker_name, value, unit, reference_range) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                [
                    (
                        str(uuid.uuid4()),
                        analysis_id,
                        marker.get("marker"),
                        str(marker.get("value")),
                        marker.get("unit"),
                        marker.get("reference_range"),
                    )
                    for marker in markers
                ],
            )
            self._conn.commit()
        logger.info(f"Saved {len(markers)} health markers for analysis {analysis_id}")

    async def delete_analysis_data(self, document_id: str) -> None:
        analysis = self._fetchone("SELECT id FROM analysis_results WHERE document_id = ?", (document_id,))
        if analysis:
            self._execute("DELETE FROM health_markers WHERE analysis_id = ?", (analysis["id"],))
            self._execute("DELETE FROM analysis_results WHERE id = ?", (analysis["id"],))
            logger.info(f"Deleted analysis data for document {document_id}")

    def load_document_data(self, document_id: str) -> Optional[Dict]:
        try:
            return self._fetchone("SELECT * FROM documents WHERE id = ?", (document_id,))
        except Exception as e:
            logger.error(f"Error loading document data for {document_id}: {e}", exc_info=True)
            return None

    def delete_document_record(self, document_id: str) -> None:
        self._execute("DELETE FROM documents WHERE id = ?", (document_id,))
        logger.info(f"Deleted document record {document_id}")

    async def list_documents(self) -> List[Dict]:
        try:
            rows = self._fetchall(self._JOIN_SELECT + " ORDER BY d.upload_date DESC")
            return [format_document_for_frontend(self._with_analysis(row)) for row in rows]
        except Exception as e:
            logger.error(f"Error listing documents: {e}", exc_info=True)
            raise

    def get_analysis(self, document_id: str) -> Optional[Dict]:
        try:
            row = self._fetchone(self._JOIN_SELECT + " WHERE d.id = ?", (document_id,))
            if not row:
                return None
            return format_document_for_frontend(self._with_analysis(row))
        except Exception as e:
            logger.error(f"Error getting analysis for {document_id}: {e}", exc_info=True)
            return None
