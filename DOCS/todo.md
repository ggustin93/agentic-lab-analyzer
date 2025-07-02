**To:** Guillaume Gustin, Senior Software Engineer
**From:** Lead Software Engineer
**Subject:** **V4 - DEFINITIVE EXECUTION PLAN:** Architecting the Lab Analyzer for IBA Expert-Level Review

Guillaume,

This is the final, definitive execution plan. It is exhaustive and contains no assumptions. Every step, code block, and rationale we have discussed is detailed below. Follow this guide precisely to build the portfolio masterpiece that will demonstrate your expert-level capabilities to IBA.

**The Narrative We Will Deliver:** *"I've architected a full-stack, enterprise-grade application that showcases modern software engineering principles. It features a decoupled, agent-based backend for processing medical documents and a highly optimized, scalable Angular 20 frontend for data visualization. The project emphasizes a clean, versioned RESTful API, real-time communication patterns using Server-Sent Events, performance-first frontend strategies, and a robust CI/CD pipeline—all of which are key requirements for the expert role at IBA."*

Let's execute.

---

### **Phase 0: Foundational Setup (30 mins)**

**Objective:** Establish a professional, clean-slate environment.

1.  **`[COMPLETED]` Isolate Work in a New Branch:**
    *   **Action:** Open your terminal in the project root.
    ```bash
    git checkout -b feature/iba-final-architecture
    ```
2.  **`[COMPLETED]` Sanitize Environment Secrets:**
    *   **Action:** Create a new file named `backend/.env`.
    *   **Action:** Add *only* the following content to it, replacing the placeholder values with your actual keys.
        ```dotenv
        # Cloud Service API Keys for the IBA MVP
        MISTRAL_API_KEY="your_mistral_api_key_here"
        CHUTES_AI_API_KEY="your_chutes_ai_api_key_here"
        ```
    *   **Action:** Verify that your top-level `.gitignore` file contains the line `.env`. If not, add it.
    *   *// Rationale: Demonstrates adherence to standard security workflows by separating configuration and secrets from code.*

---

### **Phase 1: Architecting a "Best-in-Class" Backend (2.5 hours)**

**Objective:** Showcase a decoupled, testable, and clean backend that exemplifies professional API design.

1.  **`[COMPLETED]` Prune Unused Code:**
    *   **Action:** Execute these commands from your project root to remove all unnecessary files.
    ```bash
    git rm backend/services/ocr_service.py
    git rm backend/services/ollama_service.py
    git rm backend/services/llm_service.py
    git rm backend/agents/health_analysis_agent.py
    # Also remove any tests related to these old services
    git rm backend/tests/test_config.py
    ```
2.  **`[COMPLETED]` Simplify Configuration:**
    *   **Action:** Replace the entire content of `backend/config/settings.py` with this minimal, focused code:
    ```python
    # FILE: backend/config/settings.py
    from pydantic_settings import BaseSettings, SettingsConfigDict

    class Settings(BaseSettings):
        """Application settings for the IBA MVP (Cloud-First Deployment)."""
        MISTRAL_API_KEY: str
        CHUTES_AI_API_KEY: str
        CHUTES_AI_ENDPOINT: str = "https://llm.chutes.ai/v1"
        CHUTES_AI_MODEL: str = "deepseek-ai/DeepSeek-V3-0324"
        MISTRAL_OCR_MODEL: str = "mistral-ocr-2505"
        UPLOAD_DIR: str = "uploads"
        model_config = SettingsConfigDict(env_file=".env", extra='ignore')

    settings = Settings()
    ```
3.  **`[COMPLETED]` Define Clean Architectural Boundaries (The "Protocol" Pattern):**
    *   **Action:** Create a new file `backend/agents/base.py`. This file will define the "contracts" for our AI agents.
    ```python
    # FILE: backend/agents/base.py (NEW FILE)
    from typing import Protocol
    from ..models.health_models import HealthInsights

    class OCRExtractorAgent(Protocol):
        """Defines the contract for any service that can extract text from a document."""
        async def extract_text(self, file_path: str, file_type: str) -> str:
            ...

    class LabInsightAgent(Protocol):
        """Defines the contract for any service that can analyze text and return structured insights."""
        async def analyze_text(self, raw_text: str) -> HealthInsights:
            ...
    ```
4.  **`[COMPLETED]` Refine API Data Models:**
    *   **Action:** Replace the content of `backend/models/health_models.py` to be precise and include all necessary structures.
    ```python
    # FILE: backend/models/health_models.py
    from pydantic import BaseModel, Field
    from typing import List, Optional
    from datetime import datetime

    class HealthMarker(BaseModel):
        marker: str = Field(..., description="Name of the health marker, e.g., 'Hemoglobin'")
        value: str = Field(..., description="The measured value as a string.")
        unit: Optional[str] = Field(None, description="Unit of measurement, e.g., 'g/dL'")
        reference_range: Optional[str] = Field(None, description="The normal reference range, e.g., '13.5 - 17.5'")

    class HealthDataExtraction(BaseModel):
        markers: List[HealthMarker] = Field(..., description="A list of all extracted health markers.")
        document_type: str = Field(..., description="The inferred type of document, e.g., 'Blood Test Report'")
        test_date: Optional[datetime] = Field(None, description="The date the test was performed.")

    class HealthInsights(BaseModel):
        data: HealthDataExtraction = Field(..., description="The structured data extracted from the document.")
        summary: str = Field(..., description="A brief, high-level summary of the findings.")
        key_findings: List[str] = Field(..., description="A bulleted list of the most important findings.")
        recommendations: List[str] = Field(..., description="A bulleted list of general, non-prescriptive recommendations.")
        disclaimer: str = Field(..., description="A non-negotiable medical disclaimer.")
    ```
5.  **`[COMPLETED & RE-ARCHITECTED]` Implement Concrete Agents:**
    *   **Action 1 (OCR):** The existing code in `backend/services/mistral_ocr_service.py` is good. Just ensure its `extract_text` method signature matches the `OCRExtractorAgent` protocol.
    *   **Action 2 (Insights):** Rename `backend/services/cloud_ai_service.py` to `backend/services/chutes_ai_agent.py` and replace its content.
    *   ***Design Choice & Rationale:*** *The initial plan was to use the `pydantic-ai` library for its structured output capabilities. However, this introduced significant dependency conflicts between `mistralai`, `openai`, and `httpx`. To prioritize a stable and lean MVP, a pivot was made: the `pydantic-ai` dependency was removed. The `ChutesAILabAgent` now uses the `httpx` library to directly call the Chutes.AI API, requesting a JSON object by setting the `response_format` parameter. This removes the dependency conflicts, simplifies the environment, and still enforces a structured response from the model. This decision favors stability and simplicity for the MVP over an external dependency that proved unstable in this specific context.*
    ```python
    # FILE: backend/services/chutes_ai_agent.py (RE-ARCHITECTED FOR STABILITY)
    import logging
    import json
    from typing import Optional
    import httpx
    from ..config.settings import settings
    from ..models.health_models import HealthInsights, HealthDataExtraction, HealthMarker
    from ..agents.base import LabInsightAgent

    logger = logging.getLogger(__name__)

    class ChutesAILabAgent(LabInsightAgent):
        def __init__(self):
            self.client = httpx.AsyncClient(
                base_url=settings.CHUTES_AI_ENDPOINT,
                headers={
                    "Authorization": f"Bearer {settings.CHUTES_AI_API_KEY}",
                    "Content-Type": "application/json"
                },
                timeout=30.0
            )

        async def analyze_text(self, raw_text: str) -> HealthInsights:
            logger.info(f"Analyzing text with Chutes.AI agent using model {settings.CHUTES_AI_MODEL}")
            
            system_prompt = """
            You are a highly specialized AI agent for analyzing blood test lab reports. 
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
                extraction = HealthDataExtraction(
                    markers=markers,
                    document_type=parsed_data["data"]["document_type"],
                    test_date=parsed_data["data"].get("test_date")
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
    ```
6.  **`[COMPLETED]` Implement the Orchestrator (`document_processor.py`):**
    *   **Action:** Refactored it to use the agent protocols.
    *   **Fixed Python Import Issues:** Resolved relative import errors by converting to absolute imports for better compatibility with containerized environments.

7.  **`[COMPLETED]` Implement API Versioning & Endpoints (`main.py`):**
    *   **Action:** Refactored `main.py` to use an `APIRouter` with a `/v1` prefix. Added the new `/stream` endpoint.

8.  **Implement a Critical Backend Unit Test (`backend/tests/test_document_processor.py`):**
    *   **Action:** Create the detailed unit test that mocks the agent dependencies as outlined in the V2 plan. This is a crucial piece of evidence for your testing skills.

---

### **Phase 2: Building a High-Performance, Scalable Angular Frontend (3.5 hours)**

**Objective:** Meticulously address every frontend requirement from the job spec.

1.  **`[COMPLETED]` Enforce Strict, Modern TypeScript:**
    *   **Action:** Created and updated `src/app/models/document.model.ts` with proper interfaces and a DocumentViewModel wrapper class to handle snake_case to camelCase conversion.
    *   **Fixed TypeScript Errors:** Resolved property name mismatches between frontend and backend models.

2.  **`[COMPLETED]` Optimize for Maximum Speed & Scalability:**
    *   **Action 1 (Change Detection):** Added `changeDetection: ChangeDetectionStrategy.OnPush` to the component decorators.
    *   **Action 2 (DOM Optimization):** Added `trackBy` to the `*ngFor` directives.
    *   **Action 3 (State Management):** Refactored components to use the `async` pipe with proper null handling.

3.  **`[COMPLETED]` Showcase Expert State Management & Real-Time Functionality:**
    *   **Action:** Implemented a robust, stream-focused service with EventSource for real-time updates.
    *   **Added Missing Methods:** Implemented the getDocument method in the DocumentAnalysisService.

4.  **Implement Frontend Unit Test:**
    *   **Action:** Create `src/app/services/document-analysis.service.spec.ts` with detailed tests.

---

### **Phase 3: Professional Tooling & CI/CD (1.5 hours)**

**Objective:** Prove you operate with the discipline required for large-scale enterprise development.

1.  **`[COMPLETED]` Refine Docker Configuration:**
    *   **Action:** Updated Docker configuration for better compatibility and reliability.
    *   **Fixed Health Check Issues:** Resolved container health check problems by adjusting timeouts and using appropriate tools.
    *   **Fixed Angular Builder Issues:** Resolved Angular 19 builder compatibility issues by updating the angular.json configuration.

2.  **`[COMPLETED]` Containerize for "One-Command" Reproducibility (`docker-compose.yml`):**
    *   **Action:** Cleaned the `docker-compose.yml` to only include `frontend` and `backend` services.
    *   **Action:** Added appropriate health checks and dependencies.

---

### **Phase 4: The Final Polish & Rehearsal (1 hour)**

**Objective:** Ensure a flawless presentation that tells a compelling, evidence-based story.

1.  **Craft the `README.md` as Your Presentation Guide:**
    *   **Action:** Structure it with the sections from the V2 plan. Be meticulous. Your `README.md` is your script.
2.  **Conduct a Full Dress Rehearsal:**
    *   **Action:** From a clean clone, run `docker-compose up --build`. It must work perfectly.
    *   **Action:** Practice the full demo flow:
        1.  **High-Level Intro:** Start with your polished narrative.
        2.  **Show the App:** Upload a document. Let them see the UI update in real-time via SSE.
        3.  **Dive into Frontend Code:** Show the `OnPush` strategy, the `async` pipe, the `EventSource` implementation, and the unit test.
        4.  **Dive into Backend Code:** Show the `base.py` protocols. Show the clean `DocumentProcessor`. Show the agent implementations. Show the backend unit test.
        5.  **Show the CI/CD:** Open GitHub and show them the green checkmarks from your CI pipeline runs.
        6.  **Conclude with Vision:** Talk about the "next steps" (local mode with docTR/Ollama, full WebSockets, monitoring).

This plan is your path to success. It is detailed, aggressive, and directly aligned with the expectations of an expert-level role at a company like IBA. Execute it with precision.