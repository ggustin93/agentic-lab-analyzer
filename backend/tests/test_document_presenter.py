"""
Tests for the document presenter — pure functions shaping persistence rows
into API responses (extracted from DatabaseManager, see ADR-007).
"""

from models.health_models import HealthInsights, HealthDataExtraction, HealthMarker
from services.document_presenter import format_insights_as_markdown, format_document_for_frontend


def _insights() -> HealthInsights:
    return HealthInsights(
        data=HealthDataExtraction(
            markers=[HealthMarker(marker="Hemoglobin", value="14.5", unit="g/dL",
                                  reference_range="13.0-17.5", is_out_of_range=False)],
            document_type="Blood Test Report",
        ),
        summary="All markers are within normal ranges.",
        key_findings=["All markers normal."],
        recommendations=["No action needed."],
        disclaimer="Educational purposes only.",
    )


def test_markdown_contains_all_sections_and_disclaimer():
    md = format_insights_as_markdown(_insights())
    assert "## Summary" in md
    assert "All markers are within normal ranges." in md
    assert "- All markers normal." in md
    assert "- No action needed." in md
    assert "**Disclaimer:** Educational purposes only." in md


def test_format_document_with_list_join_shape():
    """Supabase one-to-many joins return analysis_results as a list."""
    doc = {
        "id": "doc-1",
        "filename": "report.pdf",
        "upload_date": "2025-07-01T10:00:00",
        "status": "complete",
        "analysis_results": [{
            "structured_data": {"data": {"markers": [{"marker": "Hb"}]}},
            "insights": "# Report",
        }],
    }
    formatted = format_document_for_frontend(doc)
    assert formatted["document_id"] == "doc-1"
    assert formatted["uploaded_at"] == "2025-07-01T10:00:00"
    assert formatted["extracted_data"] == [{"marker": "Hb"}]
    assert formatted["ai_insights"] == "# Report"


def test_format_document_with_dict_join_shape():
    """One-to-one joins return analysis_results as a dict."""
    doc = {
        "id": "doc-2",
        "analysis_results": {
            "structured_data": {"data": {"markers": []}},
            "insights": "text",
        },
    }
    formatted = format_document_for_frontend(doc)
    assert formatted["extracted_data"] == []
    assert formatted["ai_insights"] == "text"


def test_format_document_without_analysis():
    formatted = format_document_for_frontend({"id": "doc-3", "status": "processing"})
    assert formatted["extracted_data"] == []
    assert formatted["ai_insights"] is None


def test_format_document_with_malformed_structured_data():
    """Malformed structured_data degrades to an empty marker list, never a crash."""
    doc = {"id": "doc-4", "analysis_results": [{"structured_data": {"data": "not-a-dict"}}]}
    assert format_document_for_frontend(doc)["extracted_data"] == []
