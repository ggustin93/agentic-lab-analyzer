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
    """Test successful date parsing."""
    # Test MM/DD/YYYY format
    result = parse_date("12/25/2023")
    assert result == "2023-12-25"
    
    # Test single digit month/day
    result = parse_date("1/5/2023")
    assert result == "2023-01-05"

def test_parse_date_invalid():
    """Test date parsing with invalid format."""
    # Test invalid format - should return as-is
    result = parse_date("2023-12-25")
    assert result == "2023-12-25"
    
    # Test invalid date
    result = parse_date("13/35/2023")
    assert result == "13/35/2023"

def test_parse_date_empty():
    """Test date parsing with empty values."""
    # Test None
    result = parse_date(None)
    assert result is None
    
    # Test empty string
    result = parse_date("")
    assert result is None