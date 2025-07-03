# backend/services/data_extractor_agent.py

import re
import json
import logging
import httpx
from config.settings import settings
from models.health_models import ExtractedHealthData, ExtractedHealthMarker, AnalyzedHealthData, AnalyzedHealthMarker, MarkerStatus

logger = logging.getLogger(__name__)

def clean_json_string(json_str: str) -> str:
    """Clean JSON string by removing or escaping invalid control characters."""
    if not json_str:
        return json_str
    return re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f]', '', json_str)

def safe_json_parse(json_str: str) -> dict:
    """Safely parse JSON with cleaning and error handling."""
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        cleaned_json = clean_json_string(json_str)
        try:
            return json.loads(cleaned_json)
        except json.JSONDecodeError as e:
            logger.error(f"JSON parse failed even after cleaning: {e}")
            logger.error(f"Problematic JSON (first 200 chars): {json_str[:200]}")
            raise

class LabDataExtractorAgent:
    """
    Agent responsible for two tasks:
    1. Using the Chutes.AI LLM to extract raw, structured data from text.
    2. Using Python to deterministically analyze the extracted data (e.g., check ranges).
    """
    # Pre-compile regex patterns for efficiency. This is done once when the class is defined.
    _RANGE_PATTERN = re.compile(r'(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)')
    _LT_PATTERN = re.compile(r'<=\s*(\d+(?:\.\d+)?)|<\s*(\d+(?:\.\d+)?)')
    _GT_PATTERN = re.compile(r'>=\s*(\d+(?:\.\d+)?)|>\s*(\d+(?:\.\d+)?)')
    _NUMERIC_PATTERN = re.compile(r"[-+]?\d*\.\d+|\d+")

    def __init__(self):
        self.client = httpx.AsyncClient(
            base_url=settings.CHUTES_AI_ENDPOINT,
            headers={
                "Authorization": f"Bearer {settings.CHUTES_AI_API_KEY}",
                "Content-Type": "application/json"
            },
            timeout=90.0
        )
        self.model = settings.CHUTES_AI_MODEL

    async def extract_and_analyze(self, raw_text: str) -> AnalyzedHealthData:
        """Orchestrates the extraction and analysis process."""
        logger.info("Agent 2 (Chutes.AI): Starting data extraction from raw text.")
        
        extraction_prompt = f"""
        You are an expert data extraction system for medical lab reports.
        Your ONLY task is to parse the provided text and extract all health markers into a structured JSON object.
        Your response MUST be a JSON object with this exact structure:
        {{
            "markers": [
                {{"marker": "name", "value": "value", "unit": "unit", "reference_range": "range"}}
            ],
            "document_type": "type",
            "test_date": "YYYY-MM-DD"
        }}
        - Extract values, units, and reference ranges *exactly* as they appear in the text.
        - DO NOT provide any summary, interpretation, or analysis. Your only output should be the JSON object.
        - Pay close attention to distinguishing between reference ranges and previous results.
        - Identify the overall document type (e.g., 'Blood Test Report', 'Urinalysis').
        - Extract the test date and format it as YYYY-MM-DD if available. If not available, return null for the test_date field.
        """
        
        try:
            response = await self.client.post(
                "/chat/completions",
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": f"{extraction_prompt}\n\n--- LAB REPORT TEXT ---\n{raw_text}"}],
                    "response_format": {"type": "json_object"}
                }
            )
            response.raise_for_status()
            
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            
            parsed_json = safe_json_parse(content)
            extracted_data = ExtractedHealthData(**parsed_json)
            
            logger.info(f"Agent 2 (Chutes.AI): LLM extraction complete. Found {len(extracted_data.markers)} markers.")

        except (httpx.HTTPStatusError, json.JSONDecodeError, KeyError, TypeError) as e:
            logger.error(f"Failed to extract data via Chutes.AI LLM: {e}", exc_info=True)
            return AnalyzedHealthData(markers=[], document_type="Extraction Failed", test_date=None)

        # Part 2: Deterministic analysis in Python (this part remains the same)
        analyzed_markers = [self._analyze_marker(marker) for marker in extracted_data.markers]
        logger.info("Agent 2: Python-based range analysis complete.")
        
        return AnalyzedHealthData(
            markers=analyzed_markers,
            document_type=extracted_data.document_type,
            test_date=extracted_data.test_date,
        )

    def _analyze_marker(self, marker: ExtractedHealthMarker) -> AnalyzedHealthMarker:
        """
        Analyzes a single health marker to determine if its value is low, normal, or high.
        This logic is pure Python and therefore 100% reliable.
        """
        try:
            value_str = str(marker.value).replace(',', '.') if marker.value is not None else ""
            value_match = self._NUMERIC_PATTERN.search(value_str)
            if not value_match:
                raise ValueError("No numeric value found in marker.value")
            value_float = float(value_match.group(0))
            
            if not marker.reference_range or not isinstance(marker.reference_range, str):
                raise ValueError("No reference range provided or invalid type.")

            status = self._get_status_with_severity(value_float, marker.reference_range)

        except (ValueError, TypeError, IndexError) as e:
            logger.warning(f"Could not analyze marker '{marker.marker}': {e}. Value: '{marker.value}', Range: '{marker.reference_range}'")
            status = MarkerStatus.UNKNOWN

        return AnalyzedHealthMarker(**marker.dict(), status=status)

    def _get_status_with_severity(self, value: float, reference_range: str) -> MarkerStatus:
        """
        Determines the marker status with severity (Warning/Danger) based on the reference range.

        Args:
            value: The numerical value of the marker.
            reference_range: The reference range string (e.g., "10 - 20", "<50", ">30").

        Returns:
            The calculated MarkerStatus.
        """
        # A 20% deviation threshold to distinguish warnings from dangers.
        # This is a sensible default that can be adjusted if needed.
        WARNING_THRESHOLD = 0.20 

        range_str = reference_range.replace(',', '.')

        # Use pre-compiled regex patterns
        match = self._RANGE_PATTERN.search(range_str)
        if match:
            low, high = float(match.group(1)), float(match.group(2))
            if value >= low and value <= high:
                return MarkerStatus.NORMAL
            
            range_span = high - low
            # Avoid division by zero for very narrow ranges
            warning_margin = range_span * WARNING_THRESHOLD if range_span > 0 else 0

            if value < low:
                return MarkerStatus.WARNING_LOW if (low - value) <= warning_margin else MarkerStatus.DANGER_LOW
            else: # value > high
                return MarkerStatus.WARNING_HIGH if (value - high) <= warning_margin else MarkerStatus.DANGER_HIGH

        match = self._LT_PATTERN.search(range_str)
        if match:
            high = float(match.group(1) or match.group(2))
            if value < high:
                return MarkerStatus.NORMAL
            
            warning_margin = abs(high * WARNING_THRESHOLD)
            return MarkerStatus.WARNING_HIGH if (value - high) <= warning_margin else MarkerStatus.DANGER_HIGH

        match = self._GT_PATTERN.search(range_str)
        if match:
            low = float(match.group(1) or match.group(2))
            if value > low:
                return MarkerStatus.NORMAL
            
            warning_margin = abs(low * WARNING_THRESHOLD)
            return MarkerStatus.WARNING_LOW if (low - value) <= warning_margin else MarkerStatus.DANGER_LOW

        return MarkerStatus.UNKNOWN

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose() 