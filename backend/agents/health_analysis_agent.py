from dataclasses import dataclass
from typing import List, Optional
import logging

from pydantic_ai import Agent, RunContext
from pydantic_ai.models import Model

from models.health_models import HealthDataExtraction, HealthInsights, HealthMarker

logger = logging.getLogger(__name__)

@dataclass
class HealthAnalysisDeps:
    """Dependencies for health analysis agent"""
    raw_text: str
    document_filename: str
    document_type: Optional[str] = None

# Health Data Extraction Agent
health_extraction_agent = Agent(
    model='openai:gpt-4o-mini',  # More cost-effective for extraction
    deps_type=HealthAnalysisDeps,
    output_type=HealthDataExtraction,
    system_prompt="""
    You are a medical data extraction expert. Your task is to extract structured health information 
    from medical documents with high accuracy.
    
    Guidelines:
    - Extract only clear, identifiable health markers with numeric values
    - Include units of measurement when available
    - Include reference ranges when provided
    - Identify the type of medical document (blood test, lipid panel, etc.)
    - Extract test dates if available
    - Be conservative - only extract data you're confident about
    - If no clear health markers are found, return an empty list
    """,
    instrument=True  # Enable Logfire instrumentation
)

@health_extraction_agent.system_prompt
async def add_document_context(ctx: RunContext[HealthAnalysisDeps]) -> str:
    """Add document context to the system prompt"""
    return f"""
    Document filename: {ctx.deps.document_filename}
    Document type: {ctx.deps.document_type or 'Unknown'}
    
    Please analyze the following medical document text and extract structured health data.
    """

# Health Insights Generation Agent
health_insights_agent = Agent(
    model='openai:gpt-4o',  # Use more powerful model for insights
    deps_type=HealthAnalysisDeps,
    output_type=HealthInsights,
    system_prompt="""
    You are a medical analysis expert providing educational insights about health data.
    
    Guidelines:
    - Provide clear, educational explanations of health markers
    - Identify potential areas of concern or positive findings
    - Give general health recommendations based on the data
    - Always emphasize that this is not medical advice
    - Be encouraging while being factual
    - Focus on actionable insights
    - Consider normal ranges and flag values outside normal limits
    """,
    instrument=True
)

@health_insights_agent.system_prompt
async def add_insights_context(ctx: RunContext[HealthAnalysisDeps]) -> str:
    """Add context for insights generation"""
    return f"""
    Document: {ctx.deps.document_filename}
    
    Provide educational insights about the health data found in this document.
    Remember to always include appropriate medical disclaimers.
    """

class HealthAnalysisService:
    """Service for analyzing health documents using PydanticAI agents"""
    
    def __init__(self, model_name: str = 'openai:gpt-4o-mini'):
        self.model_name = model_name
        logger.info(f"Initialized HealthAnalysisService with model: {model_name}")
    
    async def extract_health_data(
        self, 
        raw_text: str, 
        filename: str, 
        document_type: Optional[str] = None
    ) -> HealthDataExtraction:
        """Extract structured health data from raw text"""
        try:
            deps = HealthAnalysisDeps(
                raw_text=raw_text,
                document_filename=filename,
                document_type=document_type
            )
            
            result = await health_extraction_agent.run(
                user_prompt=f"Extract health data from this medical document:\n\n{raw_text}",
                deps=deps
            )
            
            logger.info(f"Successfully extracted {len(result.output.markers)} health markers")
            return result.output
            
        except Exception as e:
            logger.error(f"Health data extraction failed: {e}")
            # Return empty extraction on failure
            return HealthDataExtraction(
                markers=[],
                document_type="Unknown",
                test_date=None,
                patient_info=None
            )
    
    async def generate_insights(
        self, 
        health_data: HealthDataExtraction, 
        raw_text: str, 
        filename: str
    ) -> HealthInsights:
        """Generate AI insights from extracted health data"""
        try:
            deps = HealthAnalysisDeps(
                raw_text=raw_text,
                document_filename=filename,
                document_type=health_data.document_type
            )
            
            # Create a summary of the health data for the prompt
            markers_summary = "\n".join([
                f"- {marker.marker}: {marker.value} {marker.unit or ''} "
                f"(Reference: {marker.reference_range or 'Not provided'})"
                for marker in health_data.markers
            ])
            
            user_prompt = f"""
            Analyze these extracted health markers and provide insights:
            
            Document Type: {health_data.document_type}
            Test Date: {health_data.test_date or 'Not specified'}
            
            Health Markers:
            {markers_summary}
            
            Please provide educational insights about these results.
            """
            
            result = await health_insights_agent.run(
                user_prompt=user_prompt,
                deps=deps
            )
            
            logger.info("Successfully generated health insights")
            return result.output
            
        except Exception as e:
            logger.error(f"Insights generation failed: {e}")
            # Return fallback insights
            return HealthInsights(
                summary="Analysis completed with limited AI insights due to processing constraints.",
                key_findings=[f"Found {len(health_data.markers)} health markers in the document"],
                recommendations=["Consult with your healthcare provider to discuss these results"],
                risk_factors=[],
                follow_up_needed=True,
                disclaimer="This analysis is for educational purposes only. Always consult healthcare professionals for medical advice."
            )
    
    def is_available(self) -> bool:
        """Check if the service is available"""
        try:
            # Simple check - in production you might want to test actual API connectivity
            import openai
            return True
        except ImportError:
            return False