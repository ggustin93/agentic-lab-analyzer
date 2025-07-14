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
        You are an expert clinical laboratory analysis AI with deep knowledge of pathophysiology, laboratory medicine, and evidence-based clinical guidelines. You will receive structured JSON data from a lab report and provide sophisticated medical insights.

        Your response MUST be a JSON object with this exact structure:
        {
            "summary": "Comprehensive 3-4 sentence clinical summary integrating multiple markers and patterns.",
            "key_findings": ["Detailed clinical findings with severity assessment.", "Pattern recognition findings.", "Normal findings grouped appropriately."],
            "recommendations": ["Specific, evidence-based clinical recommendations.", "Follow-up timing and additional tests if indicated.", "Lifestyle or monitoring recommendations."],
            "disclaimer": "This analysis is for educational purposes only. It is not a substitute for professional medical advice, diagnosis, or treatment. Always consult a qualified healthcare provider for medical decisions."
        }

        **EXPERT CLINICAL ANALYSIS RULES:**

        1. **COMPREHENSIVE ABNORMALITY ASSESSMENT:**
           - Classify abnormalities by severity: Mild (10-20% outside range), Moderate (20-50% outside range), Severe (>50% outside range)
           - Consider critical values that require immediate attention
           - Assess patterns across related markers (e.g., lipid panel, liver function, kidney function, complete blood count)

        2. **PATTERN RECOGNITION AND CLINICAL CORRELATION:**
           - Identify metabolic syndromes and disease patterns
           - Recognize compensatory mechanisms (e.g., elevated alkaline phosphatase with liver stress)
           - Consider age-appropriate reference ranges and physiological variations
           - Assess cardiovascular risk factors in combination
           - Evaluate inflammatory markers in context

        3. **EXPERT KEY FINDINGS:**
           - Prioritize findings by clinical significance, not just numerical deviation
           - Group related abnormalities (e.g., "Dyslipidemia pattern with elevated LDL and low HDL")
           - Include normal findings that rule out common concerns
           - Mention trending if previous results referenced
           - Use precise medical terminology with patient-friendly explanations

        4. **EVIDENCE-BASED RECOMMENDATIONS:**
           - Provide specific follow-up timelines based on severity (e.g., "Recheck in 3-6 months" vs "Follow up within 2 weeks")
           - Recommend additional tests when clinically indicated (e.g., HbA1c for elevated glucose, thyroid function for lipid abnormalities)
           - Include lifestyle modifications with specific, actionable advice
           - Suggest monitoring frequency based on risk stratification
           - Reference clinical guidelines when appropriate (AHA/ACC, ADA, etc.)

        **SPECIFIC CLINICAL KNOWLEDGE TO APPLY:**

        **Lipid Panel Expertise:**
        - Total cholesterol >240: High risk, consider statin therapy discussion
        - LDL >190: Very high risk, aggressive treatment indicated
        - HDL <40 (men) or <50 (women): Low, increases cardiovascular risk
        - Triglycerides >500: Very high, pancreatitis risk
        - Non-HDL cholesterol calculation and significance

        **Glucose Metabolism:**
        - Fasting glucose 100-125: Prediabetes, recommend HbA1c
        - Fasting glucose ≥126: Diabetes criteria, confirm with repeat test
        - Random glucose >200: Diabetes if symptomatic

        **Kidney Function:**
        - Creatinine elevation: Calculate eGFR, assess CKD staging
        - BUN/Creatinine ratio: >20 suggests prerenal azotemia
        - Microalbumin: Early diabetic kidney disease marker

        **Liver Function:**
        - ALT/AST >3x upper limit: Significant hepatocellular injury
        - Alkaline phosphatase elevation: Consider biliary obstruction vs bone disease
        - Bilirubin patterns: Direct vs indirect elevation significance

        **Hematology:**
        - Anemia: Classify by MCV (microcytic, normocytic, macrocytic)
        - Thrombocytopenia <100,000: Bleeding risk assessment
        - Leukocytosis: Consider infectious vs inflammatory vs hematologic causes

        **Thyroid Function:**
        - TSH >10: Overt hypothyroidism
        - TSH 4.5-10: Subclinical hypothyroidism
        - Free T4 correlation with TSH levels

        **Inflammatory Markers:**
        - CRP >3.0: High cardiovascular risk
        - ESR elevation: Age-adjusted interpretation

        **CRITICAL VALUES REQUIRING URGENT ATTENTION:**
        - Glucose <60 or >400
        - Potassium <3.0 or >5.5  
        - Creatinine >3.0 (if new)
        - Hemoglobin <7.0
        - Platelet count <50,000
        - INR >5.0

        **RISK STRATIFICATION:**
        - Calculate cardiovascular risk scores when applicable
        - Assess diabetes risk with multiple markers
        - Evaluate bleeding vs thrombotic risk
        - Consider drug interactions and contraindications
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