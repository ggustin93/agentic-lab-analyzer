import pytest
import json
from services.json_utils import clean_json_string, safe_json_parse, parse_date

def test_clean_json_string():
    """Test JSON string cleaning functionality."""
    # Test with clean JSON
    clean_json = '{"key": "value"}'
    assert clean_json_string(clean_json) == clean_json
    
    # Test with control characters
    dirty_json = '{"key": "value\x00\x01"}'
    cleaned = clean_json_string(dirty_json)
    assert '\x00' not in cleaned
    assert '\x01' not in cleaned
    
    # Test with empty string
    assert clean_json_string("") == ""
    
    # Test with None
    assert clean_json_string(None) == None

def test_safe_json_parse_success():
    """Test successful JSON parsing."""
    valid_json = '{"key": "value", "number": 42}'
    result = safe_json_parse(valid_json)
    
    assert isinstance(result, dict)
    assert result["key"] == "value"
    assert result["number"] == 42

def test_safe_json_parse_with_cleaning():
    """Test JSON parsing with cleaning."""
    dirty_json = '{"key": "value\x00", "number": 42}'
    result = safe_json_parse(dirty_json)
    
    assert isinstance(result, dict)
    assert result["key"] == "value"
    assert result["number"] == 42

def test_safe_json_parse_failure():
    """Test JSON parsing failure."""
    invalid_json = '{"key": "value", "number": 42'  # Missing closing brace
    
    with pytest.raises(json.JSONDecodeError):
        safe_json_parse(invalid_json)

def test_parse_date_success():
    """Valid ISO 8601 dates pass through unchanged."""
    assert parse_date("2023-12-25") == "2023-12-25"
    assert parse_date("2025-04-03") == "2025-04-03"

def test_parse_date_rejects_ambiguous_formats():
    """
    Slash formats are ambiguous (03/04/2025 is April 3rd in Belgium but
    March 4th in the US): anything non-ISO must be rejected, never guessed.
    """
    assert parse_date("03/04/2025") is None
    assert parse_date("12/25/2023") is None

def test_parse_date_invalid():
    """Garbage and impossible dates are rejected as None."""
    assert parse_date("not-a-date") is None
    assert parse_date("2023-13-45") is None

def test_parse_date_empty():
    """Test date parsing with empty values."""
    # Test None
    result = parse_date(None)
    assert result is None
    
    # Test empty string
    result = parse_date("")
    assert result is None