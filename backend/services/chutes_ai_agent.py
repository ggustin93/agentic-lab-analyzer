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
        
        # --- AGENT RESPONSIBILITY DISCLAIMER ---
        # For this MVP, this agent is responsible for BOTH data extraction and insight generation.
        # In a production system, these would ideally be two separate, specialized agents:
        # 1. Extraction Agent: Focuses only on parsing the raw text into the structured `data` object.
        # 2. Insight Agent: Receives the structured `data` and generates `summary`, `key_findings`, and `recommendations`.
        # This consolidated approach is a deliberate choice for simplicity in the MVP.
        # --- END DISCLAIMER ---
        
        system_prompt = """
        You are a highly specialized AI agent for analyzing blood test lab reports and give expert and actionable medical interpretation. 
        Your response MUST be a JSON object following this exact structure:
        {
            "data": {
                "markers": [{"marker": "name", "value": "value", "unit": "unit", "reference_range": "range"}],
                "document_type": "type",
                "test_date": null
            },
            "summary": "Brief summary of the most important findings.",
            "key_findings": ["Clear, concise finding about a specific marker or group of markers.", "Another key finding."],
            "recommendations": ["Actionable recommendation related to a key finding.", "Another recommendation."],
            "disclaimer": "This analysis is for educational purposes only. It is not a substitute for professional medical advice. Always consult a qualified healthcare provider."
        }

        **ANALYSIS AND INSIGHTS GENERATION RULES:**
        1.  **Analyze All Markers**: Review every marker provided in the lab report.
        2.  **Identify Abnormalities**: Compare each marker's `value` against its `reference_range`. Identify and prioritize any values that are outside of the normal range (high or low).
        3.  **Generate Summary**: Write a brief, neutral summary (2-3 sentences) of the overall results, highlighting whether they are generally normal or if there are noteworthy findings.
        4.  **Create Key Findings**: For each abnormal marker, create a clear, concise "key finding". If all markers are normal, state that clearly as the key finding.
            - *Example (Abnormal)*: "The Creatinine level (1.4 mg/dL) is slightly elevated above the reference range (0.70 - 1.30 mg/dL), which may suggest further evaluation of kidney function is needed."
            - *Example (Normal)*: "All markers, including Hemoglobin and Glucose, are within their respective normal reference ranges."
        5.  **Provide Recommendations**: For each key finding about an abnormal value, provide a sensible, non-prescriptive recommendation.
            - *Example*: "Discuss the elevated Creatinine level with a healthcare provider to determine if further testing is necessary."
        
        **CRITICAL COLUMN IDENTIFICATION AND DATA EXTRACTION RULES:**
        When analyzing lab reports with multiple columns, carefully distinguish between:

        1.  **REFERENCE RANGES ("Normes" / "Normal" / "Reference"):**
            - These are the CURRENT medical standard ranges.
            - Extract EXACTLY as they appear for the `reference_range` field.

        2.  **PREVIOUS RESULTS ("Résultats Antérieurs" / "Previous Results"):**
            - These are HISTORICAL test values.
            - **DO NOT** use these as reference ranges. They are the patient's past data, not medical standards.

        3.  **CURRENT VALUES ("Résultats" / "Results"):**
            - These are the CURRENT test results being analyzed
            - Use these for the `value` field

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

        CRITICAL: CLEAN UP MALFORMED OCR PATTERNS:
        When you encounter malformed reference ranges from OCR, clean them up:
        
        MALFORMED PATTERNS TO FIX:
        - "<6 - 6.0" → Should be "<6.0" (upper bound only)
        - "<2 - 2.0" → Should be "<2.0" (upper bound only)  
        - "<0 - 0.50" → Should be "<0.50" (upper bound only)
        - "<5 - 5.0" → Should be "<5.0" (upper bound only)
        
        CLEANING RULES:
        1. If you see pattern like "<X - Y" where X ≤ Y, extract as "<Y" (use the higher value)
        2. If you see pattern like ">X - Y" where X ≥ Y, extract as ">X" (use the higher value)
        3. Remove redundant formatting: "< 6.0 - 6.0" → "<6.0"
        4. Preserve proper ranges: "3.5 - 5.0" → Keep as "3.5 - 5.0" (this is correct)
        
        EXAMPLES OF PROPER CLEANING:
        - OCR gives: "<6 - 6.0" → Extract: "<6.0"
        - OCR gives: "<2 - 2.0" → Extract: "<2.0"
        - OCR gives: "<0 - 0.50" → Extract: "<0.50"
        - OCR gives: "3.5 - 5.0" → Extract: "3.5 - 5.0" (keep as-is, this is correct)
        - OCR gives: "> 40 - 40" → Extract: ">40"
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
            
            if not insights.summary or insights.summary == "No summary available" or not insights.key_findings:
                logger.warning("AI response was valid JSON but contained no summary or key findings.")
            
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