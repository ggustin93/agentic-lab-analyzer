# backend/services/extraction_agent.py
import logging
import httpx
from config.settings import settings
from models.health_models import HealthDataExtraction
from services.chutes_ai_agent import safe_json_parse, parse_date

logger = logging.getLogger(__name__)

class ExtractionAgent:
    def __init__(self):
        self.client = httpx.AsyncClient(
            base_url=settings.CHUTES_AI_ENDPOINT,
            headers={
                "Authorization": f"Bearer {settings.CHUTES_AI_API_KEY}",
                "Content-Type": "application/json"
            },
            timeout=60.0
        )
        # For extraction, a smaller, faster model is often sufficient and more cost-effective.
        # We'll use the same model for now, but this architecture allows for easy swapping.
        self.model = settings.CHUTES_AI_MODEL 

    async def extract_data(self, raw_text: str) -> HealthDataExtraction:
        logger.info(f"Extracting structured data with model {self.model}")

        system_prompt = """
        You are a highly specialized data extraction AI. Your ONLY task is to extract health markers from raw text and return a structured JSON object. You MUST NOT generate summaries, findings, or recommendations.

        Your response MUST be a JSON object following this exact structure:
        {
            "markers": [{"marker": "name", "value": "value", "unit": "unit", "reference_range": "range"}],
            "document_type": "type",
            "test_date": "MM/DD/YYYY"
        }

        **CRITICAL EXTRACTION RULES:**
        1.  **Identify Columns:** Carefully distinguish between "Results" (current values), "Reference Ranges", and "Previous Results". NEVER use previous results as reference ranges.
        2.  **Extract Ranges Exactly:** Preserve the exact format of the reference range (e.g., "3.5 - 5.0", "< 2.0"). If a range is missing, return an empty string for that field.
        3.  **Clean Malformed OCR:** Fix common OCR errors. For example:
            - "<6 - 6.0" should become "<6.0"
            - ">40 - 40" should become ">40"
            - "3.5 - 5.0" should remain "3.5 - 5.0" (this is correct)
        4.  **Value and Unit:** Extract the marker's value and unit into their respective fields.

        **UNIT FORMATTING RULES (VERY IMPORTANT):**
        1.  **Use Plain Text First:** For common units, use simple text (e.g., "mg/dL", "g/dL", "%").
        2.  **Use Unicode for Special Characters:** For Greek letters, use the actual Unicode character. GOOD: "/μL", BAD: "/\\mu L".
        3.  **Use ^ for Powers:** For exponents, use the caret symbol. GOOD: "10^3/mm^3", BAD: "10³/mm³".
        4.  **DO NOT** use LaTeX commands like `\mathrm`, `\mu`, or delimiters like `$`. The frontend will handle formatting.
        
        **Examples of CORRECT unit formatting:**
        - "mmol/L"
        - "mg/dL"
        - "%"
        - "/μL"
        - "10^6/mm^3"
        """
        
        try:
            response = await self.client.post(
                "/chat/completions",
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"Extract data from this text:\n\n{raw_text}"}
                    ],
                    "response_format": {"type": "json_object"}
                }
            )
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"]
            parsed_data = safe_json_parse(content)
            
            # Add a date parsing step
            parsed_data['test_date'] = parse_date(parsed_data.get('test_date'))

            return HealthDataExtraction(**parsed_data)

        except Exception as e:
            logger.error(f"Critical failure in ExtractionAgent: {e}", exc_info=True)
            raise

    async def close(self):
        await self.client.aclose()