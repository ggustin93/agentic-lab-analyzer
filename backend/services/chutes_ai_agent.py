"""
Chutes AI Agent Service
Cloud AI service implementation for Chutes.ai integration
"""

import logging
import json
from typing import Optional
from datetime import datetime
import httpx
from config.settings import settings
from models.health_models import HealthInsights, HealthDataExtraction, HealthMarker
from agents.base import LabInsightAgent

logger = logging.getLogger(__name__)

def parse_date(date_str: Optional[str]) -> Optional[str]:
    """Parse date from MM/DD/YYYY to YYYY-MM-DD."""
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, "%m/%d/%Y").strftime("%Y-%m-%d")
    except ValueError:
        logger.warning(f"Could not parse date: {date_str}. Returning as is.")
        return date_str

class ChutesAILabAgent(LabInsightAgent):
    def __init__(self):
        self.client = httpx.AsyncClient(
            base_url=settings.CHUTES_AI_ENDPOINT,
            headers={
                "Authorization": f"Bearer {settings.CHUTES_AI_API_KEY}",
                "Content-Type": "application/json"
            },
            timeout=90.0
        )

    async def analyze_text(self, raw_text: str) -> HealthInsights:
        logger.info(f"Analyzing text with Chutes.AI agent using model {settings.CHUTES_AI_MODEL}")
        
        system_prompt = """
        You are a highly specialized AI agent for analyzing blood test lab reports. 
        Extract structured information and return it as a JSON object with this exact structure:
        {
            "data": {
                "markers": [{"marker": "name", "value": "value", "unit": "unit", "reference_range": "range"}],
                "document_type": "type",
                "test_date": null
            },
            "summary": "Brief summary",
            "key_findings": ["finding1", "finding2"],
            "recommendations": ["rec1", "rec2"],
            "disclaimer": "This analysis is for educational purposes only. It is not a substitute for professional medical advice. Always consult a qualified healthcare provider."
        }

        CRITICAL INSTRUCTIONS FOR REFERENCE RANGE EXTRACTION:

        1. PRESERVE EXACT TEXT: Extract reference ranges exactly as they appear in the document, including spacing, punctuation, and formatting.

        2. COMMON RANGE FORMATS TO RECOGNIZE:
           - "3.5-5.0" or "3.5 - 5.0" 
           - "< 2.0" or "<2.0"
           - "> 10" or ">10"
           - "2.0-4.5 mg/dL"
           - "Normal: 65-100"
           - "Ref: 4.0-6.0"
           - "Range: 2.1-5.4"
           - "(3.1-5.2)"
           - "3.5 to 5.0"
           - "Below 2.0"
           - "Above 100"

        3. WHEN RANGES ARE UNCLEAR OR MISSING:
           - If no clear range is visible, use empty string: ""
           - If range is partially visible but incomplete (e.g., "3.5-..."), use empty string: ""
           - If range is corrupted by OCR (e.g., "3.§-5.0"), use empty string: ""
           - Only extract what you can clearly see and understand

        4. UNIT HANDLING:
           - Extract units separately from ranges when possible
           - If units are embedded in range (e.g., "3.5-5.0 mg/dL"), extract range as "3.5-5.0" and unit as "mg/dL"
           - If units are unclear, extract the full text including units in the range field

        5. CONTEXT CLUES:
           - Look for words like "Reference:", "Normal:", "Range:", "Ref:", before range values
           - Check for ranges in parentheses next to marker names
           - Look for ranges in separate columns or sections

        6. QUALITY OVER QUANTITY:
           - It's better to return an empty reference_range than an incorrect one
           - The frontend has fallback ranges for common markers when extraction fails
           - Focus on accuracy and preserving exactly what's in the document
        """

        try:
            response = await self.client.post(
                "/chat/completions",
                json={
                    "model": settings.CHUTES_AI_MODEL,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"Analyze this lab report text:\n\n{raw_text}"}
                    ],
                    "response_format": {"type": "json_object"}
                }
            )
            response.raise_for_status()
            
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            parsed_data = json.loads(content)
            
            # Convert to our Pydantic models
            markers = [HealthMarker(**marker) for marker in parsed_data["data"]["markers"]]
            
            # Log reference range extraction quality
            total_markers = len(markers)
            markers_with_ranges = len([m for m in markers if m.reference_range and m.reference_range.strip()])
            range_extraction_rate = (markers_with_ranges / total_markers * 100) if total_markers > 0 else 0
            
            logger.info(f"Extracted {total_markers} markers, {markers_with_ranges} with reference ranges ({range_extraction_rate:.1f}%)")
            
            if markers_with_ranges < total_markers:
                missing_ranges = [m.marker for m in markers if not m.reference_range or not m.reference_range.strip()]
                logger.debug(f"Markers without reference ranges: {missing_ranges}")
            
            parsed_test_date = parse_date(parsed_data["data"].get("test_date"))

            extraction = HealthDataExtraction(
                markers=markers,
                document_type=parsed_data["data"]["document_type"],
                test_date=parsed_test_date
            )
            
            insights = HealthInsights(
                data=extraction,
                summary=parsed_data["summary"],
                key_findings=parsed_data["key_findings"],
                recommendations=parsed_data["recommendations"],
                disclaimer=parsed_data["disclaimer"]
            )
            
            if not insights.data.markers:
                logger.warning("Chutes.AI returned a valid structure but no markers were extracted.")
            
            return insights
            
        except Exception as e:
            logger.error(f"Critical failure in Chutes.AI agent: {e}", exc_info=True)
            raise

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()