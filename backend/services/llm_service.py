import openai
import os
import logging
from typing import Dict, List, Optional
import json
import asyncio
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger(__name__)

class LLMService:
    """Service for LLM-based analysis of health documents"""
    
    def __init__(self):
        self.client = None
        self.api_key = os.getenv('OPENAI_API_KEY')
        self.model = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
        self.max_tokens = int(os.getenv('MAX_TOKENS', '2000'))
        
        if self.api_key:
            openai.api_key = self.api_key
            self.client = openai.OpenAI(api_key=self.api_key)
    
    def is_available(self) -> bool:
        """Check if LLM service is available"""
        return self.client is not None and self.api_key is not None
    
    async def extract_health_data(self, raw_text: str) -> List[Dict]:
        """Extract structured health data from raw text"""
        try:
            if not self.is_available():
                return self._fallback_extraction(raw_text)
            
            prompt = self._create_extraction_prompt(raw_text)
            
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a medical data extraction expert. Extract health markers, values, units, and reference ranges from medical documents."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=0.1
            )
            
            result = response.choices[0].message.content
            return self._parse_extraction_result(result)
            
        except Exception as e:
            logger.error(f"LLM extraction error: {e}")
            return self._fallback_extraction(raw_text)
    
    async def generate_insights(self, extracted_data: List[Dict], raw_text: str) -> str:
        """Generate AI insights from extracted health data"""
        try:
            if not self.is_available():
                return self._fallback_insights(extracted_data)
            
            prompt = self._create_insights_prompt(extracted_data, raw_text)
            
            response = await asyncio.to_thread(
                self.client.chat.completions.create,
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a medical analysis expert. Provide educational insights about health data while emphasizing this is not medical advice."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=self.max_tokens,
                temperature=0.3
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"LLM insights error: {e}")
            return self._fallback_insights(extracted_data)
    
    def _create_extraction_prompt(self, raw_text: str) -> str:
        """Create prompt for data extraction"""
        return f"""
Extract health markers and their values from the following medical document text. 
Return the data in JSON format with the following structure:

[
  {{
    "marker": "Test Name",
    "value": "Numeric Value",
    "unit": "Unit of Measurement",
    "referenceRange": "Normal Range"
  }}
]

Only extract clear, identifiable health markers with numeric values. 
If a reference range is not provided, use null.

Medical Document Text:
{raw_text}

JSON Response:
"""
    
    def _create_insights_prompt(self, extracted_data: List[Dict], raw_text: str) -> str:
        """Create prompt for insights generation"""
        data_summary = json.dumps(extracted_data, indent=2)
        
        return f"""
Based on the following extracted health data, provide educational insights in markdown format.

IMPORTANT: Always include a disclaimer that this is not medical advice and users should consult healthcare professionals.

Structure your response with:
1. Summary of findings
2. Analysis of key markers
3. General health recommendations
4. Important disclaimers

Extracted Data:
{data_summary}

Provide insights in markdown format:
"""
    
    def _parse_extraction_result(self, result: str) -> List[Dict]:
        """Parse LLM extraction result"""
        try:
            # Try to extract JSON from the response
            start_idx = result.find('[')
            end_idx = result.rfind(']') + 1
            
            if start_idx != -1 and end_idx != -1:
                json_str = result[start_idx:end_idx]
                return json.loads(json_str)
            
            return []
            
        except Exception as e:
            logger.error(f"Failed to parse extraction result: {e}")
            return []
    
    def _fallback_extraction(self, raw_text: str) -> List[Dict]:
        """Fallback extraction when LLM is not available"""
        # Simple pattern-based extraction as fallback
        fallback_data = []
        
        # This is a very basic fallback - in production, you'd want more sophisticated parsing
        lines = raw_text.split('\n')
        for line in lines:
            line = line.strip()
            if ':' in line and any(char.isdigit() for char in line):
                parts = line.split(':')
                if len(parts) >= 2:
                    marker = parts[0].strip()
                    value_part = parts[1].strip()
                    
                    # Extract numeric value
                    import re
                    numbers = re.findall(r'\d+\.?\d*', value_part)
                    if numbers:
                        fallback_data.append({
                            "marker": marker,
                            "value": numbers[0],
                            "unit": None,
                            "referenceRange": None
                        })
        
        return fallback_data
    
    def _fallback_insights(self, extracted_data: List[Dict]) -> str:
        """Fallback insights when LLM is not available"""
        return f"""# Health Data Analysis

## Summary
We have extracted {len(extracted_data)} health markers from your document.

## Extracted Markers
{chr(10).join([f"- **{item['marker']}**: {item['value']} {item.get('unit', '')}" for item in extracted_data])}

## Important Disclaimer
⚠️ **This is not medical advice.** The information provided is for educational purposes only. 
Always consult a qualified healthcare professional regarding any health concerns or before making any 
decisions related to your health or treatment.

## Recommendations
- Review these results with your healthcare provider
- Keep track of your health markers over time
- Follow up on any values outside normal ranges

*Note: AI-powered analysis is currently unavailable. This is a basic summary of your extracted data.*
"""