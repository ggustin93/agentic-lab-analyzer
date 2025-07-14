# backend/services/insight_agent.py
import logging
import httpx
from config.settings import settings
from models.health_models import HealthInsights, HealthDataExtraction
from services.json_utils import safe_json_parse

logger = logging.getLogger(__name__)

class InsightAgent:
    def __init__(self):
        self.client = httpx.AsyncClient(
            base_url=settings.CHUTES_AI_ENDPOINT,
            headers={
                "Authorization": f"Bearer {settings.CHUTES_AI_API_KEY}",
                "Content-Type": "application/json"
            },
            timeout=60.0
        )
        # For insight generation, a more powerful model is often better.
        self.model = settings.CHUTES_AI_MODEL 

    async def generate_insights(self, extracted_data: HealthDataExtraction) -> HealthInsights:
        logger.info(f"Generating insights with model {self.model}")
        
        system_prompt = """
        You are a medical analysis AI. You will receive structured JSON data from a lab report. Your task is to generate a high-level summary, key findings, and general recommendations based ONLY on the provided data.

        Your response MUST be a JSON object with this exact structure:
        {
            "summary": "Brief, high-level summary of the findings.",
            "key_findings": ["A bulleted list of the most important findings.", "Another key finding."],
            "recommendations": ["A bulleted list of general, non-prescriptive recommendations.", "Another recommendation."],
            "disclaimer": "This analysis is for educational purposes only. It is not a substitute for professional medical advice. Always consult a qualified healthcare provider."
        }

        **ANALYSIS RULES:**
        1.  **Analyze Abnormalities:** Review the `markers`. For each marker, compare its `value` to its `reference_range` to identify high or low values.
        2.  **Generate Summary:** Write a 2-3 sentence summary of the overall results.
        3.  **Create Key Findings:** Create a bullet point for each abnormal marker. If all markers are normal, state that clearly as the key finding.
            - Example (Abnormal): "The Creatinine level (1.4 mg/dL) is slightly elevated above the reference range (0.70 - 1.30 mg/dL)."
        4.  **Provide Recommendations:** For each finding about an abnormal value, provide a sensible, non-prescriptive recommendation.
            - Example: "Discuss the elevated Creatinine level with a healthcare provider."
        """
        
        # Convert the Pydantic object back to a dict for the prompt
        input_json_string = extracted_data.model_dump_json(indent=2)
        
        try:
            response = await self.client.post(
                "/chat/completions",
                json={
                    "model": self.model,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"Generate insights for this structured lab data:\n\n{input_json_string}"}
                    ],
                    "response_format": {"type": "json_object"}
                }
            )
            response.raise_for_status()
            content = response.json()["choices"][0]["message"]["content"]
            insight_data = safe_json_parse(content)

            # Combine the input data with the generated insights
            return HealthInsights(data=extracted_data, **insight_data)
            
        except Exception as e:
            logger.error(f"Critical failure in InsightAgent: {e}", exc_info=True)
            raise

    async def close(self):
        await self.client.aclose()