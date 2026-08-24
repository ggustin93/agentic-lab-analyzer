"""
JSON and Data Parsing Utilities

Utility functions for safely parsing JSON and handling data transformations.
These functions are shared across multiple agent implementations.
"""

import json
import logging
import re
from typing import Optional
from datetime import datetime

logger = logging.getLogger(__name__)


def clean_json_string(json_str: str) -> str:
    """
    Clean JSON string by removing or escaping invalid control characters.
    
    Args:
        json_str: Raw JSON string that may contain invalid characters
        
    Returns:
        Cleaned JSON string safe for parsing
    """
    if not json_str:
        return json_str
    
    # Remove null bytes and other control characters that are invalid in JSON.
    # Deliberately nothing else: rewriting escape sequences (e.g. \" -> ") can
    # corrupt strings that were valid all along, which is worse than failing.
    return re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', json_str)


def safe_json_parse(json_str: str) -> dict:
    """
    Safely parse JSON with cleaning and error handling.
    
    Args:
        json_str: JSON string to parse
        
    Returns:
        Parsed JSON as dictionary
        
    Raises:
        json.JSONDecodeError: If parsing fails even after cleaning
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
    """
    Validate an ISO 8601 (YYYY-MM-DD) date string.

    The extraction prompt requires ISO 8601 precisely because slash formats are
    ambiguous (03/04/2025 is April 3rd in Belgium, March 4th in the US) and a
    silently swapped day/month is a data-integrity error on medical data.
    Anything that is not a valid ISO date is therefore rejected as None —
    "unknown" is always safer than "guessed".

    Args:
        date_str: Candidate date string from the extraction model, or None

    Returns:
        The validated YYYY-MM-DD string, or None if absent/invalid
    """
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, "%Y-%m-%d").strftime("%Y-%m-%d")
    except ValueError:
        logger.warning(f"Rejecting non-ISO test_date from extraction output: {date_str!r}")
        return None