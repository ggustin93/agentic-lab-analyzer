"""
Chutes AI Agent Service
Cloud AI service implementation for Chutes.ai integration
"""

import logging
import json
from typing import Optional
from datetime import datetime
import httpx
from config.settings import settings
from models.health_models import HealthInsights, HealthDataExtraction, HealthMarker
from agents.base import LabInsightAgent

logger = logging.getLogger(__name__)

def parse_date(date_str: Optional[str]) -> Optional[str]:
    """Parse date from MM/DD/YYYY to YYYY-MM-DD."""
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, "%m/%d/%Y").strftime("%Y-%m-%d")
    except ValueError:
        logger.warning(f"Could not parse date: {date_str}. Returning as is.")
        return date_str

class ChutesAILabAgent(LabInsightAgent):
    def __init__(self):
        self.client = httpx.AsyncClient(
            base_url=settings.CHUTES_AI_ENDPOINT,
            headers={
                "Authorization": f"Bearer {settings.CHUTES_AI_API_KEY}",
                "Content-Type": "application/json"
            },
            timeout=90.0
        )

    async def analyze_text(self, raw_text: str) -> HealthInsights:
        logger.info(f"Analyzing text with Chutes.AI agent using model {settings.CHUTES_AI_MODEL}")
        
        system_prompt = """
        You are MedAnalyzer AI, an elite medical document analysis expert with PhD-level expertise in clinical laboratory medicine, hematology, biochemistry, endocrinology, and preventive medicine. You possess the analytical capabilities of a board-certified pathologist combined with the nutritional expertise of a registered dietitian specializing in therapeutic nutrition.

        ## YOUR EXPERTISE DOMAINS:
        **Clinical Laboratory Medicine**: Complete Blood Count, Basic/Comprehensive Metabolic Panels, Lipid Profiles, Liver Function Tests, Thyroid Function, Cardiac Markers, Inflammatory Biomarkers, Coagulation Studies
        **Hematology**: Iron studies, B12/Folate analysis, Complete Blood Count interpretation, anemia classification, hemoglobinopathies
        **Biochemistry**: Glucose metabolism, HbA1c interpretation, kidney function markers, electrolyte balance, enzyme analysis
        **Endocrinology**: Thyroid hormones (TSH, T3, T4), diabetes markers, hormone panels, vitamin D metabolism, parathyroid function
        **Cardiology**: Lipid metabolism, cardiovascular risk stratification, troponins, BNP/NT-proBNP, homocysteine
        **Nutritional Medicine**: Micronutrient deficiencies, therapeutic nutrition, evidence-based dietary interventions, supplement protocols
        **Pharmacokinetics**: Drug-nutrient interactions, absorption optimization, bioavailability enhancement

        ## CRITICAL ANALYSIS RULES:
        ⚠️ **NEVER HALLUCINATE DATA** - Extract ONLY information explicitly present in the provided OCR text
        ⚠️ **NO ASSUMPTIONS** - If a value, unit, or reference range is not clearly stated, mark as null or "not specified"
        ⚠️ **PRECISE EXTRACTION** - Use exact values, units, and reference ranges as they appear in the document
        ⚠️ **DATA INTEGRITY** - Preserve original formatting and terminology from the lab report

        Extract structured information and return it as a JSON object with this exact structure:
        {
            "data": {
                "markers": [{"marker": "name", "value": "value", "unit": "unit", "reference_range": "range"}],
                "document_type": "type",
                "test_date": null
            },
            "summary": "Brief summary",
            "key_findings": ["finding1", "finding2"],
            "recommendations": ["rec1", "rec2"],
            "disclaimer": "This analysis is for educational purposes only. It is not a substitute for professional medical advice. Always consult a qualified healthcare provider."
        }

        For recommendations, provide SPECIFIC and ACTIONABLE dietary advice based on the lab results:
        - Include specific foods to eat or avoid
        - Mention exact nutrients, vitamins, or minerals needed
        - Suggest meal timing, portion sizes, or preparation methods when relevant
        - Reference specific dietary patterns (Mediterranean, DASH, etc.) if appropriate
        - Include hydration recommendations if relevant
        - Be concrete: instead of "eat healthy foods", say "consume 2-3 servings of fatty fish per week (salmon, mackerel) for omega-3 fatty acids"
        - For high cholesterol: specify "limit saturated fat to <7% of daily calories, increase soluble fiber to 10-25g daily through oats, beans, and apples"
        - For diabetes/glucose issues: mention "choose low glycemic index foods like quinoa instead of white rice, aim for 25-30g fiber daily"
        - For iron deficiency: "consume vitamin C-rich foods (citrus, bell peppers) with iron-rich meals to enhance absorption"
        """

        try:
            response = await self.client.post(
                "/chat/completions",
                json={
                    "model": settings.CHUTES_AI_MODEL,
                    "messages": [
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"Analyze this lab report text:\n\n{raw_text}"}
                    ],
                    "response_format": {"type": "json_object"}
                }
            )
            response.raise_for_status()
            
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            parsed_data = json.loads(content)
            
            # Convert to our Pydantic models
            markers = [HealthMarker(**marker) for marker in parsed_data["data"]["markers"]]
            
            parsed_test_date = parse_date(parsed_data["data"].get("test_date"))

            extraction = HealthDataExtraction(
                markers=markers,
                document_type=parsed_data["data"]["document_type"],
                test_date=parsed_test_date
            )
            
            insights = HealthInsights(
                data=extraction,
                summary=parsed_data["summary"],
                key_findings=parsed_data["key_findings"],
                recommendations=parsed_data["recommendations"],
                disclaimer=parsed_data["disclaimer"]
            )
            
            if not insights.data.markers:
                logger.warning("Chutes.AI returned a valid structure but no markers were extracted.")
            
            return insights
            
        except Exception as e:
            logger.error(f"Critical failure in Chutes.AI agent: {e}", exc_info=True)
            raise

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()