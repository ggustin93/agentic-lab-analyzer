# backend/services/clinical_insight_agent.py

import logging
import json
import httpx
from config.settings import settings
from models.health_models import AnalyzedHealthData, MarkerStatus

logger = logging.getLogger(__name__)

class ClinicalInsightAgent:
    """
    Agent responsible for generating high-level clinical insights based on
    pre-analyzed, structured data. This agent acts like a physician interpreter
    and uses the Chutes.AI service.
    """
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

    async def generate_insights(self, analyzed_data: AnalyzedHealthData) -> dict:
        """
        Generates summary, findings, and recommendations as a dictionary.
        This decouples the agent from the final output model.
        """
        logger.info("Agent 3 (Chutes.AI): Starting clinical insight generation.")
        
        # Filter for any markers that are not 'normal'.
        out_of_range_markers = [m for m in analyzed_data.markers if m.status != MarkerStatus.NORMAL]
        
        if not out_of_range_markers:
            # If all markers are normal, we can return a standard success response
            return {
                "summary": "All lab markers are within their normal reference ranges.",
                "key_findings": ["All markers are within normal limits."],
                "recommendations": ["Continue with your healthy lifestyle. No specific recommendations based on these results."],
                "disclaimer": "This analysis is for educational purposes only. It is not a substitute for professional medical advice, diagnosis, or treatment. Always consult a qualified healthcare provider with any questions you may have regarding a medical condition."
            }

        # Build a detailed context string for the prompt, explaining the severity levels.
        prompt_context_lines = [
            f"- {m.marker}: {m.value} {m.unit} (Status: {m.status.value}, Normal Range: {m.reference_range})"
            for m in out_of_range_markers
        ]
        prompt_context = "The following markers were outside their normal reference ranges:\n" + "\n".join(prompt_context_lines)

        insight_prompt = f"""
        You are a compassionate, board-certified physician explaining lab results to a patient.
        Your focus is on providing actionable, non-prescriptive lifestyle and dietary advice. Your tone should be educational and reassuring.

        The patient's results have been analyzed with the following severity levels:
        - 'warning_low' or 'warning_high': The value is slightly outside the normal range. This is a point of attention but not immediate alarm.
        - 'danger_low' or 'danger_high': The value is significantly outside the normal range and warrants more serious attention.

        Based on the following summary, please provide a JSON response with three keys: "summary", "key_findings", and "recommendations".
        1.  In the "summary", provide a high-level overview.
        2.  In "key_findings", create a bulleted list. Distinguish between 'warning' and 'danger' levels in your language.
        3.  In "recommendations", provide a bulleted list of lifestyle/dietary advice. Tailor the urgency and nature of the recommendations to the severity of the findings. For 'danger' levels, strongly suggest consulting a doctor.

        **CRITICAL INSTRUCTIONS:**
        - Your response MUST be a valid JSON object.
        - DO NOT provide a diagnosis or suggest specific medical treatments.
        - Always include the provided medical disclaimer verbatim.

        --- PATIENT LAB DATA SUMMARY ---
        Document Type: {analyzed_data.document_type}
        {prompt_context}
        --- END OF DATA ---
        """
        
        try:
            response = await self.client.post(
                "/chat/completions",
                json={
                    "model": self.model,
                    "messages": [{"role": "user", "content": insight_prompt}],
                    "response_format": {"type": "json_object"}
                }
            )
            response.raise_for_status()
            
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            
            # Return the parsed JSON content directly as a dictionary
            return json.loads(content)

        except (httpx.HTTPStatusError, json.JSONDecodeError, KeyError, TypeError) as e:
            logger.error(f"Failed to generate insights via Chutes.AI LLM: {e}", exc_info=True)
            # Fallback to a safe error response
            return {
                "summary": "Could not generate AI insights due to a technical error.",
                "key_findings": ["Error during analysis."],
                "recommendations": ["Please try again later."],
                "disclaimer": "An error occurred during processing."
            }

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose() 