# backend/services/extraction_agent.py
import logging
import httpx
from config.settings import settings
from models.health_models import HealthDataExtraction
from services.json_utils import safe_json_parse, parse_date
import json
from typing import Dict

logger = logging.getLogger(__name__)

class ExtractionAgent:
    """Agent specialized in extracting structured data from OCR text using Mistral AI."""

    def __init__(self):
        """Initializes the ExtractionAgent."""
        self.client = httpx.AsyncClient(
            base_url="https://api.mistral.ai/v1",
            headers={"Authorization": f"Bearer {settings.MISTRAL_API_KEY}"},
            timeout=120
        )
        self.model = "mistral-large-latest"
        logger.info(f"ExtractionAgent initialized with model: {self.model}")

    async def extract_data(self, structured_ocr_data: Dict) -> HealthDataExtraction:
        logger.info(f"Extracting structured data with model {self.model}")

        system_prompt = """
        You are a hyper-specialized data extraction AI. Your task is to parse a JSON object from an OCR service and extract health markers from the markdown content within it.

        **INPUT FORMAT:**
        You will receive a JSON object from the Mistral OCR API. It contains a list of pages, and each page has a 'markdown' field with the content.
        Example:
        {
          "pages": [
            { "index": 0, "markdown": "| Marker | Value | Reference |\\n|---|---|---|\\n| Hemoglobin | 14.5 | 13.0-17.5 |" },
            { "index": 1, "markdown": "| Platelets | 250 | 150-450 |" }
          ]
        }

        **OUTPUT FORMAT:**
        Your response MUST be a JSON object following this exact structure:
        {
            "markers": [{"marker": "name", "value": "value", "unit": "unit", "reference_range": "range", "is_out_of_range": true/false}],
            "document_type": "type",
            "test_date": "MM/DD/YYYY"
        }

        **CRITICAL EXTRACTION RULES:**
        1.  **Parse the Markdown:** Accurately parse the markdown tables in the `markdown` field of each page. The table structure is your primary source of truth for associating values with their correct columns.
        2.  **Column Identification:** Carefully identify the columns for the marker name, the current result value, the unit, and the reference range. The reference range column is often named "Normes", "Valeurs de référence", or "Reference Range".
        3.  **Handling Multiple Value Columns & Historical Data**:
            - Your primary goal is to extract the **MOST RECENT** lab result.
            - If the table has multiple columns with patient results, and one is clearly labeled as historical (e.g., with a past date in the header), you **MUST** ignore the historical column.
            - If there are multiple result columns without clear date headers, **assume the leftmost result column is the most recent value.** You must ignore all other result columns.
            - Results might contain non-numeric characters like trend arrows (e.g., '↗ 205', '↘ 80'). You **MUST** strip these characters and any surrounding whitespace before extracting the numeric value. For '↗ 205', extract '205'.
        4.  **Out of Range Flag (`is_out_of_range`):**
            - This is a CRITICAL rule. For reports from "CLINIQUES ST LUC", the presence of a `↗` or `↘` arrow next to a value **definitively means that value is out of the normal reference range.**
            - When you see a `↗` or `↘` in the original OCR text for a value, you **MUST** set `is_out_of_range` to `true` for that marker.
            - If no arrow is present, you must compare the extracted numeric `value` against the `reference_range` to determine if it is out of range. Set `is_out_of_range` to `false` if it is within the normal range or if you cannot confidently determine its status.
        5.  **Extract Ranges Exactly:** Preserve the exact format of the reference range (e.g., "3.5 - 5.0", "< 2.0"). If a range is missing, return an empty string.
        6.  **Handle Multi-Page Tables:** Data for a single marker might span across pages. Be prepared to correlate information if necessary.

        **UNIT FORMATTING RULES (VERY IMPORTANT):**
        1.  **Use Plain Text First:** For common units, use simple text (e.g., "mg/dL", "g/dL", "%").
        2.  **Use Unicode for Special Characters:** For Greek letters, use the actual Unicode character. GOOD: "/μL", BAD: "/\\muL".
        3.  **Use ^ for Powers:** For exponents, use the caret symbol. GOOD: "10^3/mm^3", BAD: "10³/mm³".
        4.  **DO NOT** use LaTeX commands or `$` delimiters.

        Now, analyze the provided OCR JSON and extract the data.
        """
        
        # Convert the structured OCR data dict to a JSON string for the prompt
        ocr_json_string = json.dumps(structured_ocr_data, indent=2)

        try:
            response = await self.client.post(
                "/chat/completions",
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"Extract data from this OCR JSON output:\n\n{ocr_json_string}"}
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