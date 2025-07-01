"""
Ollama Service Implementation
Provides local AI using Ollama with PydanticAI integration
"""

import logging
from typing import Optional
from dataclasses import dataclass

from pydantic_ai import Agent, RunContext
from pydantic_ai.models.openai import OpenAIModel
from pydantic_ai.providers.openai import OpenAIProvider

from models.health_models import HealthDataExtraction, HealthInsights, HealthMarker
from config.settings import settings

logger = logging.getLogger(__name__)

@dataclass
class OllamaHealthAnalysisDeps:
    """Dependencies for Ollama health analysis agent"""
    raw_text: str
    document_filename: str
    document_type: Optional[str] = None

class OllamaService:
    """Local AI service using Ollama"""
    
    def __init__(self):
        self.base_url = settings.ollama_base_url
        self.extraction_model = settings.ollama_model
        self.insights_model = settings.ollama_insights_model
        
        # Create Ollama models for PydanticAI
        self.extraction_ollama_model = OpenAIModel(
            model_name=self.extraction_model,
            provider=OpenAIProvider(base_url=f'{self.base_url}/v1')
        )
        
        self.insights_ollama_model = OpenAIModel(
            model_name=self.insights_model,
            provider=OpenAIProvider(base_url=f'{self.base_url}/v1')
        )
        
        # Create PydanticAI agents
        self.extraction_agent = Agent(
            model=self.extraction_ollama_model,
            deps_type=OllamaHealthAnalysisDeps,
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
            instrument=settings.enable_monitoring
        )
        
        self.insights_agent = Agent(
            model=self.insights_ollama_model,
            deps_type=OllamaHealthAnalysisDeps,
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
            instrument=settings.enable_monitoring
        )
        
        logger.info(f"Initialized OllamaService with base_url: {self.base_url}")
    
    def is_available(self) -> bool:
        """Check if Ollama service is available"""
        try:
            import httpx
            response = httpx.get(f"{self.base_url}/api/tags", timeout=5.0)
            return response.status_code == 200
        except Exception as e:
            logger.warning(f"Ollama not available: {e}")
            return False
    
    async def extract_health_data(
        self, 
        raw_text: str, 
        filename: str, 
        document_type: Optional[str] = None
    ) -> HealthDataExtraction:
        """Extract structured health data using Ollama"""
        try:
            deps = OllamaHealthAnalysisDeps(
                raw_text=raw_text,
                document_filename=filename,
                document_type=document_type
            )
            
            result = await self.extraction_agent.run(
                user_prompt=f"Extract health data from this medical document:\n\n{raw_text}",
                deps=deps
            )
            
            logger.info(f"Successfully extracted {len(result.output.markers)} health markers using Ollama")
            return result.output
            
        except Exception as e:
            logger.error(f"Ollama health data extraction failed: {e}")
            # Return empty extraction on failure
            return HealthDataExtraction(
                markers=[],
                document_type=document_type or "Unknown",
                test_date=None,
                patient_info=None
            )
    
    async def generate_insights(
        self, 
        health_data: HealthDataExtraction, 
        raw_text: str, 
        filename: str
    ) -> HealthInsights:
        """Generate AI insights using Ollama"""
        try:
            deps = OllamaHealthAnalysisDeps(
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
            
            result = await self.insights_agent.run(
                user_prompt=user_prompt,
                deps=deps
            )
            
            logger.info("Successfully generated health insights using Ollama")
            return result.output
            
        except Exception as e:
            logger.error(f"Ollama insights generation failed: {e}")
            # Return fallback insights
            return HealthInsights(
                summary="Analysis completed using local Ollama AI.",
                key_findings=[f"Found {len(health_data.markers)} health markers in the document"],
                recommendations=["Consult with your healthcare provider to discuss these results"],
                risk_factors=[],
                follow_up_needed=True,
                disclaimer="This analysis is for educational purposes only. Always consult healthcare professionals for medical advice."
            )
    
    def get_model_info(self) -> dict:
        """Get information about available Ollama models"""
        try:
            import httpx
            response = httpx.get(f"{self.base_url}/api/tags")
            if response.status_code == 200:
                return response.json()
            return {"models": []}
        except Exception as e:
            logger.error(f"Failed to get Ollama model info: {e}")
            return {"models": [], "error": str(e)}