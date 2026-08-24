"""
Document presenter: shapes persistence-layer data for the frontend.

Pure functions, deliberately free of I/O: presentation concerns used to live
inside DatabaseManager, which mixed the persistence layer with API-response
shaping (a single-responsibility violation noted in the project's own
audit). Keeping them pure also makes them trivially unit-testable.
"""

from typing import Dict, List, Optional

from models.health_models import HealthInsights


def format_insights_as_markdown(insights: HealthInsights) -> str:
    """Convert structured insights to the markdown shown by the frontend."""
    md = f"# Analysis Report\n\n## Summary\n{insights.summary}\n\n"
    md += "## Key Findings\n" + "".join([f"- {finding}\n" for finding in insights.key_findings])
    md += "\n## Recommendations\n" + "".join([f"- {rec}\n" for rec in insights.recommendations])
    md += f"\n---\n\n**Disclaimer:** {insights.disclaimer}"
    return md


def format_document_for_frontend(doc: Dict) -> Dict:
    """Shape a raw document row (with joined analysis) into the API response."""
    analysis_results = doc.get("analysis_results")
    analysis: Optional[Dict] = None

    # Handle both list (one-to-many) and dict (one-to-one) from Supabase join
    if isinstance(analysis_results, list) and len(analysis_results) > 0:
        analysis = analysis_results[0]
    elif isinstance(analysis_results, dict):
        analysis = analysis_results

    extracted_data: List[Dict] = []
    ai_insights = None

    if analysis:
        structured_data = analysis.get("structured_data")
        ai_insights = analysis.get("insights")

        # Safely extract markers for the frontend
        if isinstance(structured_data, dict) and isinstance(structured_data.get("data"), dict):
            extracted_data = structured_data["data"].get("markers", [])

    return {
        "id": doc.get("id"),
        "document_id": doc.get("id"),
        "filename": doc.get("filename"),
        "uploaded_at": doc.get("upload_date"),
        "status": doc.get("status"),
        "processed_at": doc.get("processed_at"),
        "public_url": doc.get("public_url"),
        "raw_text": doc.get("raw_text"),
        "extracted_data": extracted_data,
        "ai_insights": ai_insights,
        "error_message": doc.get("error_message"),
        "progress": doc.get("progress"),
        "processing_stage": doc.get("processing_stage"),
    }
