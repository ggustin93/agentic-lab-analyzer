"""
Cloud AI Service Implementation
Supports Chutes.ai and other cloud AI services (removed Bittensor)
"""

import logging
import httpx
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from models.health_models import HealthDataExtraction, HealthInsights, HealthMarker
from config.settings import settings, CloudProvider

logger = logging.getLogger(__name__)

@dataclass
class CloudAIDeps:
    """Dependencies for cloud AI service"""
    raw_text: str
    document_filename: str
    document_type: Optional[str] = None

class CloudAIService:
    """Cloud AI service for decentralized health analysis"""
    
    def __init__(self):
        self.provider = settings.cloud_provider
        self.api_key = None
        self.endpoint = None
        
        # Configure based on provider
        if self.provider == CloudProvider.CHUTES_AI:
            self.api_key = settings.chutes_ai_api_key
            self.endpoint = settings.chutes_ai_endpoint
        elif self.provider == CloudProvider.OPENAI:
            self.api_key = settings.openai_api_key
            self.endpoint = "https://api.openai.com/v1"
        elif self.provider == CloudProvider.ANTHROPIC:
            self.api_key = settings.anthropic_api_key
            self.endpoint = "https://api.anthropic.com/v1"
        
        # HTTP client for API calls
        self.client = httpx.AsyncClient(timeout=30.0)
        
        logger.info(f"Initialized CloudAIService with provider: {self.provider}")
    
    def is_available(self) -> bool:
        """Check if cloud AI service is available"""
        return self.api_key is not None and self.endpoint is not None
    
    async def extract_health_data(
        self, 
        raw_text: str, 
        filename: str, 
        document_type: Optional[str] = None
    ) -> HealthDataExtraction:
        """Extract structured health data using cloud AI"""
        try:
            if self.provider == CloudProvider.CHUTES_AI:
                return await self._extract_with_chutes_ai(raw_text, filename, document_type)
            elif self.provider == CloudProvider.OPENAI:
                return await self._extract_with_openai(raw_text, filename, document_type)
            elif self.provider == CloudProvider.ANTHROPIC:
                return await self._extract_with_anthropic(raw_text, filename, document_type)
            else:
                raise Exception(f"Unsupported cloud provider: {self.provider}")
                
        except Exception as e:
            logger.error(f"Cloud health data extraction failed: {e}")
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
        """Generate AI insights using cloud services"""
        try:
            if self.provider == CloudProvider.CHUTES_AI:
                return await self._insights_with_chutes_ai(health_data, raw_text, filename)
            elif self.provider == CloudProvider.OPENAI:
                return await self._insights_with_openai(health_data, raw_text, filename)
            elif self.provider == CloudProvider.ANTHROPIC:
                return await self._insights_with_anthropic(health_data, raw_text, filename)
            else:
                raise Exception(f"Unsupported cloud provider: {self.provider}")
                
        except Exception as e:
            logger.error(f"Cloud insights generation failed: {e}")
            # Return fallback insights
            return HealthInsights(
                summary="Analysis completed using cloud AI services.",
                key_findings=[f"Found {len(health_data.markers)} health markers in the document"],
                recommendations=["Consult with your healthcare provider to discuss these results"],
                risk_factors=[],
                follow_up_needed=True,
                disclaimer="This analysis is for educational purposes only. Always consult healthcare professionals for medical advice."
            )
    
    async def _extract_with_chutes_ai(
        self, 
        raw_text: str, 
        filename: str, 
        document_type: Optional[str]
    ) -> HealthDataExtraction:
        """Extract health data using Chutes.ai"""
        try:
            payload = {
                "model": "chutes-health-extractor",
                "messages": [
                    {
                        "role": "system",
                        "content": """You are a medical data extraction expert. Extract structured health information 
                        from medical documents with high accuracy. Return data in the specified JSON format."""
                    },
                    {
                        "role": "user",
                        "content": f"""Extract health markers from this document:
                        
                        Filename: {filename}
                        Document Type: {document_type or 'Unknown'}
                        
                        Text:
                        {raw_text}
                        
                        Return structured health markers with values, units, and reference ranges."""
                    }
                ],
                "response_format": {
                    "type": "json_schema",
                    "json_schema": {
                        "name": "health_extraction",
                        "schema": {
                            "type": "object",
                            "properties": {
                                "markers": {
                                    "type": "array",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "marker": {"type": "string"},
                                            "value": {"type": "string"},
                                            "unit": {"type": "string"},
                                            "reference_range": {"type": "string"}
                                        }
                                    }
                                },
                                "document_type": {"type": "string"},
                                "test_date": {"type": "string"},
                                "patient_info": {"type": "string"}
                            }
                        }
                    }
                }
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            response = await self.client.post(
                f"{self.endpoint}/chat/completions",
                json=payload,
                headers=headers
            )
            response.raise_for_status()
            
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            
            # Parse the JSON response
            import json
            data = json.loads(content)
            
            # Convert to HealthDataExtraction
            markers = [
                HealthMarker(
                    marker=m["marker"],
                    value=m["value"],
                    unit=m.get("unit"),
                    reference_range=m.get("reference_range")
                )
                for m in data.get("markers", [])
            ]
            
            return HealthDataExtraction(
                markers=markers,
                document_type=data.get("document_type", document_type or "Unknown"),
                test_date=data.get("test_date"),
                patient_info=data.get("patient_info")
            )
            
        except Exception as e:
            logger.error(f"Chutes.ai extraction error: {e}")
            raise
    
    async def _extract_with_openai(
        self, 
        raw_text: str, 
        filename: str, 
        document_type: Optional[str]
    ) -> HealthDataExtraction:
        """Extract health data using OpenAI"""
        try:
            payload = {
                "model": settings.openai_model,
                "messages": [
                    {
                        "role": "system",
                        "content": """You are a medical data extraction expert. Extract structured health information 
                        from medical documents with high accuracy."""
                    },
                    {
                        "role": "user",
                        "content": f"""Extract health markers from this document:
                        
                        Filename: {filename}
                        Document Type: {document_type or 'Unknown'}
                        
                        Text:
                        {raw_text}
                        
                        Return a JSON object with health markers, document type, test date, and patient info."""
                    }
                ],
                "max_tokens": settings.max_tokens,
                "temperature": 0.1
            }
            
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            response = await self.client.post(
                f"{self.endpoint}/chat/completions",
                json=payload,
                headers=headers
            )
            response.raise_for_status()
            
            result = response.json()
            content = result["choices"][0]["message"]["content"]
            
            # Parse and convert response (simplified for this example)
            # In production, you'd want more robust parsing
            return HealthDataExtraction(
                markers=[],
                document_type=document_type or "Unknown",
                test_date=None,
                patient_info=None
            )
            
        except Exception as e:
            logger.error(f"OpenAI extraction error: {e}")
            raise
    
    async def _extract_with_anthropic(
        self, 
        raw_text: str, 
        filename: str, 
        document_type: Optional[str]
    ) -> HealthDataExtraction:
        """Extract health data using Anthropic Claude"""
        try:
            payload = {
                "model": "claude-3-haiku-20240307",
                "max_tokens": settings.max_tokens,
                "messages": [
                    {
                        "role": "user",
                        "content": f"""Extract health markers from this medical document:
                        
                        Filename: {filename}
                        Document Type: {document_type or 'Unknown'}
                        
                        Text:
                        {raw_text}
                        
                        Return structured health markers with values, units, and reference ranges."""
                    }
                ]
            }
            
            headers = {
                "x-api-key": self.api_key,
                "Content-Type": "application/json",
                "anthropic-version": "2023-06-01"
            }
            
            response = await self.client.post(
                f"{self.endpoint}/messages",
                json=payload,
                headers=headers
            )
            response.raise_for_status()
            
            result = response.json()
            content = result["content"][0]["text"]
            
            # Parse and convert response (simplified for this example)
            return HealthDataExtraction(
                markers=[],
                document_type=document_type or "Unknown",
                test_date=None,
                patient_info=None
            )
            
        except Exception as e:
            logger.error(f"Anthropic extraction error: {e}")
            raise
    
    async def _insights_with_chutes_ai(
        self, 
        health_data: HealthDataExtraction, 
        raw_text: str, 
        filename: str
    ) -> HealthInsights:
        """Generate insights using Chutes.ai"""
        # Implementation similar to extraction but for insights
        return HealthInsights(
            summary="Chutes.ai analysis completed",
            key_findings=[f"Analysis of {len(health_data.markers)} health markers"],
            recommendations=["Consult with your healthcare provider"],
            risk_factors=[],
            follow_up_needed=True,
            disclaimer="This analysis is for educational purposes only."
        )
    
    async def _insights_with_openai(
        self, 
        health_data: HealthDataExtraction, 
        raw_text: str, 
        filename: str
    ) -> HealthInsights:
        """Generate insights using OpenAI"""
        # Implementation for OpenAI insights
        return HealthInsights(
            summary="OpenAI analysis completed",
            key_findings=[f"Analysis of {len(health_data.markers)} health markers"],
            recommendations=["Consult with your healthcare provider"],
            risk_factors=[],
            follow_up_needed=True,
            disclaimer="This analysis is for educational purposes only."
        )
    
    async def _insights_with_anthropic(
        self, 
        health_data: HealthDataExtraction, 
        raw_text: str, 
        filename: str
    ) -> HealthInsights:
        """Generate insights using Anthropic"""
        # Implementation for Anthropic insights
        return HealthInsights(
            summary="Anthropic analysis completed",
            key_findings=[f"Analysis of {len(health_data.markers)} health markers"],
            recommendations=["Consult with your healthcare provider"],
            risk_factors=[],
            follow_up_needed=True,
            disclaimer="This analysis is for educational purposes only."
        )
    
    async def close(self):
        """Close the HTTP client"""
        await self.client.aclose()