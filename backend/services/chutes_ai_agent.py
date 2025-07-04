"""
Chutes AI Agent Service
Cloud AI service implementation for Chutes.ai integration
"""

import logging
import json
import re
from typing import Optional
from datetime import datetime
import httpx
from config.settings import settings
from models.health_models import HealthInsights, HealthDataExtraction, HealthMarker
from agents.base import LabInsightAgent

logger = logging.getLogger(__name__)

def clean_json_string(json_str: str) -> str:
    """
    Clean JSON string by removing or escaping invalid control characters.
    """
    if not json_str:
        return json_str
    
    # Remove or replace problematic control characters
    # Keep only valid JSON control characters: \", \\, \/, \b, \f, \n, \r, \t
    cleaned = json_str
    
    # Remove null bytes and other control characters except valid JSON ones
    cleaned = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', cleaned)
    
    # Fix common issues with quotes and backslashes
    cleaned = cleaned.replace('\\"', '"').replace('\\\\', '\\')
    
    return cleaned

def safe_json_parse(json_str: str) -> dict:
    """
    Safely parse JSON with cleaning and error handling.
    """
    try:
        # First attempt: direct parsing
        return json.loads(json_str)
    except json.JSONDecodeError as e:
        logger.warning(f"Initial JSON parse failed: {e}")
        
        # Second attempt: clean and parse
        try:
            cleaned_json = clean_json_string(json_str)
            return json.loads(cleaned_json)
        except json.JSONDecodeError as e2:
            logger.error(f"JSON parse failed after cleaning: {e2}")
            logger.error(f"Problematic JSON content (first 500 chars): {json_str[:500]}")
            logger.error(f"Problematic JSON content around error position: {json_str[max(0, e.pos-50):e.pos+50]}")
            raise e2

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

        CRITICAL COLUMN IDENTIFICATION RULES:
        When analyzing lab reports with multiple columns, carefully distinguish between:

        1. REFERENCE RANGES ("Normes" / "Normal" / "Reference"):
           - These are the CURRENT medical standard ranges for each test
           - Usually appear as ranges like "13.0 - 17.5", "< 100", "> 40", "Normal: 65-100"
           - Extract EXACTLY as they appear in the document
           - Use these for the "reference_range" field

        2. PREVIOUS RESULTS ("Résultats Antérieurs" / "Previous Results"):
           - These are HISTORICAL test values from past dates
           - Often include dates like "17/05/2021" or specific values from previous tests
           - DO NOT use these as reference ranges
           - These are patient's own historical data, not medical standards

        3. CURRENT VALUES ("Résultats" / "Results"):
           - These are the CURRENT test results being analyzed
           - Use these for the "value" field

        EXAMPLES OF CORRECT EXTRACTION:
        - If you see: "Hémoglobine | 16.1 | g/dL | 13.0 - 17.5 | 16.3"
          Extract: {"marker": "Hémoglobine", "value": "16.1", "unit": "g/dL", "reference_range": "13.0 - 17.5"}
          NOT: {"reference_range": "16.3"} (this is a previous result!)

        - If you see: "VGM | 91.9 | μm³ | 80.0 - 98.0 | 95.2"
          Extract: {"marker": "VGM", "value": "91.9", "unit": "μm³", "reference_range": "80.0 - 98.0"}
          NOT: {"reference_range": "95.2"} (this is a previous result!)

        REFERENCE RANGE QUALITY REQUIREMENTS:
        - Preserve exact formatting from the document (including spaces, dashes, symbols)
        - Common formats: "3.5-5.0", "< 2.0", "> 40", "Normal: 65-100", "40.0 - 54.0"
        - If unclear or missing, return empty string for reference_range
        - Never guess or approximate ranges
        - Never use previous results as reference ranges
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
            
            # Safe JSON parsing with cleaning
            parsed_data = safe_json_parse(content)
            
            # Validate structure
            if not isinstance(parsed_data, dict):
                raise ValueError("Parsed data is not a dictionary")
            
            if "data" not in parsed_data or "markers" not in parsed_data["data"]:
                raise ValueError("Missing required 'data.markers' structure in response")
            
            # Convert to our Pydantic models
            markers = []
            for marker_data in parsed_data["data"]["markers"]:
                try:
                    marker = HealthMarker(**marker_data)
                    markers.append(marker)
                except Exception as e:
                    logger.warning(f"Failed to create HealthMarker from {marker_data}: {e}")
                    continue
            
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
                document_type=parsed_data["data"].get("document_type", "Lab Report"),
                test_date=parsed_test_date
            )
            
            insights = HealthInsights(
                data=extraction,
                summary=parsed_data.get("summary", "No summary available"),
                key_findings=parsed_data.get("key_findings", []),
                recommendations=parsed_data.get("recommendations", []),
                disclaimer=parsed_data.get("disclaimer", "This analysis is for educational purposes only. Always consult a qualified healthcare provider.")
            )
            
            if not insights.data.markers:
                logger.warning("Chutes.AI returned a valid structure but no markers were extracted.")
            
            return insights
            
        except json.JSONDecodeError as e:
            logger.error(f"JSON parsing failed in Chutes.AI agent: {e}", exc_info=True)
            logger.error(f"Raw response content: {content if 'content' in locals() else 'Not available'}")
            raise Exception(f"Failed to parse AI response: {e}")
        except KeyError as e:
            logger.error(f"Missing expected key in Chutes.AI response: {e}", exc_info=True)
            logger.error(f"Response structure: {result if 'result' in locals() else 'Not available'}")
            raise Exception(f"Invalid response structure from AI: {e}")
        except Exception as e:
            logger.error(f"Critical failure in Chutes.AI agent: {e}", exc_info=True)
            raise

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()