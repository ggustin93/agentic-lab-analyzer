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
    Parse date from MM/DD/YYYY to YYYY-MM-DD format.
    
    Args:
        date_str: Date string in MM/DD/YYYY format or None
        
    Returns:
        Date string in YYYY-MM-DD format or original string if parsing fails
    """
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, "%m/%d/%Y").strftime("%Y-%m-%d")
    except ValueError:
        logger.warning(f"Could not parse date: {date_str}. Returning as is.")
        return date_str