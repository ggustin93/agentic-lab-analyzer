
---

### **Implementation Plan: Professionalizing the DocBot AI Application**

**Objective:** To implement three high-impact improvements that enhance the application's architecture, maintainability, and production-readiness.

---

### **Quick Win 1: Architectural Refinement - Implement an LLM Chain of Responsibility**

**A. The Goal:**
We will refactor the single, monolithic AI agent (`ChutesAILabAgent`) into two smaller, specialized agents. This pattern is called a "Chain of Responsibility."
1.  **Extraction Agent:** Its only job is to read raw text and extract structured `HealthMarker` data.
2.  **Insight Agent:** Its only job is to take the structured data from the first agent and generate the `summary`, `key_findings`, and `recommendations`.

**B. The "Why":**
*   **Maintainability:** Smaller, focused prompts are much easier to debug and improve than one giant prompt.
*   **Cost & Performance:** We can use a faster, cheaper AI model for the simple task of extraction and a more powerful model for the complex task of analysis.
*   **Robustness:** If data extraction fails, we know exactly where the process broke down, and we don't waste time or money attempting to generate insights from bad data.

**C. Step-by-Step Implementation:**

**Step 1.1: Create the Extraction Agent**

Create a new file: `backend/services/extraction_agent.py`

Copy and paste the following code into it. This agent is highly specialized for JSON extraction.

```python
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
```

**Step 1.2: Create the Insight Agent**

Create a new file: `backend/services/insight_agent.py`

Copy and paste the following code. This agent receives structured data, making its job much simpler.

```python
# backend/services/insight_agent.py
import logging
import httpx
from config.settings import settings
from models.health_models import HealthInsights, HealthDataExtraction
from services.chutes_ai_agent import safe_json_parse

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
```

**Step 1.3: Update the `DocumentProcessor` to use the new agents**

Open the file: `backend/services/document_processor.py`

Make the following changes:

1.  **Import the new agents** at the top of the file:
    ```python
    # ... other imports
    from .mistral_ocr_service import MistralOCRService
    # REMOVE the old ChutesAILabAgent import
    # from .chutes_ai_agent import ChutesAILabAgent 
    # ADD the new agent imports
    from .extraction_agent import ExtractionAgent
    from .insight_agent import InsightAgent
    ```
2.  **Update the `__init__` method** to use the new agents:
    ```python
    class DocumentProcessor:
        # ...
        def __init__(self):
            """Initialize the document processor with OCR and AI analysis agents."""
            self.ocr_agent: OCRExtractorAgent = MistralOCRService()
            # REPLACE the single insight_agent with two specialized agents
            # self.insight_agent: LabInsightAgent = ChutesAILabAgent()
            self.extraction_agent = ExtractionAgent()
            self.insight_agent = InsightAgent()
            self.supabase: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)
            self.bucket_name = settings.SUPABASE_BUCKET_NAME
    ```
3.  **Update the `_execute_analysis_stage` method** to call the agents in a chain:
    ```python
    # Find this method and replace its content
    async def _execute_analysis_stage(self, document_id: str, raw_text: str) -> HealthInsights:
        """
        Execute AI analysis stage with progress tracking.
        
        Args:
            document_id: ID of the document being processed
            raw_text: Extracted text content from OCR stage
            
        Returns:
            HealthInsights: Structured health insights from AI analysis
        """
        # --- Stage 2a: Data Extraction ---
        logger.info(f"🧠 Stage 2a/4: Starting Data Extraction for {document_id} ({len(raw_text)} chars)")
        self._update_processing_stage(document_id, ProcessingStage.AI_ANALYSIS, {"raw_text": raw_text, "progress": 30})
        extracted_data = await self.extraction_agent.extract_data(raw_text)
        if not extracted_data.markers:
            logger.warning(f"ExtractionAgent returned no markers for document {document_id}")
            # Optional: you could raise an error here if no markers is a critical failure
            # raise ValueError("Extraction process yielded no health markers")

        # --- Stage 2b: Insight Generation ---
        logger.info(f"🧠 Stage 2b/4: Starting Insight Generation for {document_id}")
        self._update_processing_stage(document_id, ProcessingStage.AI_ANALYSIS, {"progress": 50})
        insights_result = await self.insight_agent.generate_insights(extracted_data)
        
        return insights_result
    ```

**Step 1.4: Clean up**

*   You can now safely delete the `backend/services/chutes_ai_agent.py` file, as its logic has been split into the two new agents. Or, rename it to `_legacy_chutes_ai_agent.py` if you want to keep it for reference.

**D. Verification:**
1.  Run the application (`docker-compose up`).
2.  Upload a document.
3.  Check the backend logs. You should now see new log messages:
    *   `INFO:services.extraction_agent:Extracting structured data with model...`
    *   `INFO:services.insight_agent:Generating insights with model...`
4.  The final analysis on the frontend should still look complete, with both the data table and the AI insights populated correctly.

---

### **Quick Win 2: Improving Frontend Separation of Concerns**

**A. The Goal:**
To move complex business logic out of the UI component (`DataTableComponent`) and into a dedicated service (`LabMarkerInfoService`). The component should only be responsible for *displaying* data, not *interpreting* it.

**B. The "Why":**
*   **Separation of Concerns (SoC):** This is a core software engineering principle. It makes code cleaner and easier to understand.
*   **Testability:** It's much easier to write automated tests for a service method than for a UI component method.
*   **Reusability:** The clinical logic can now be reused by other parts of the application without duplicating code.

**C. Step-by-Step Implementation:**

**Step 2.1: Move the Logic to the Service**

Open the file `src/app/services/lab-marker-info.service.ts`

Add the following new public method to the `LabMarkerInfoService` class. You can copy the logic directly from the component.

```typescript
// src/app/services/lab-marker-info.service.ts
import { Injectable } from '@angular/core';
import { HealthMarker } from '../models/document.model'; // Make sure HealthMarker is imported

// ... existing interface and class definition ...

@Injectable({
  providedIn: 'root'
})
export class LabMarkerInfoService {
  // ... existing labMarkers property and methods ...
  
  // ADD THIS NEW METHOD
  public getMarkerClinicalStatus(item: HealthMarker): 'normal' | 'borderline' | 'abnormal' {
    const comparisonRange = this.getComparisonReferenceRange(item);
    
    if (!comparisonRange || !item.value) {
      return 'normal';
    }

    const value = parseFloat(item.value);
    if (isNaN(value)) {
      return 'normal';
    }

    if (comparisonRange.includes('...') || 
        comparisonRange.includes('depending') || 
        comparisonRange.length < 2) {
      return 'normal';
    }

    let match = comparisonRange.match(/^(\d+(?:\.\d+)?)\s*[-–—]\s*(\d+(?:\.\d+)?)$/);
    if (match) {
        const min = parseFloat(match[1]);
        const max = parseFloat(match[2]);
        const rangeSize = max - min;
        const tolerance = rangeSize * 0.25;

        if (value >= min && value <= max) return 'normal';
        if (value < min) return (min - value) <= tolerance ? 'borderline' : 'abnormal';
        if (value > max) return (value - max) <= tolerance ? 'borderline' : 'abnormal';
    }

    match = comparisonRange.match(/^[<≤]\s*(\d+(?:\.\d+)?)$/);
    if (match) {
        const max = parseFloat(match[1]);
        const tolerance = max * 0.25;
        if (value < max) return 'normal';
        return (value - max) <= tolerance ? 'borderline' : 'abnormal';
    }
    
    match = comparisonRange.match(/^<(\d+(?:\.\d+)?)\s*-\s*(\d+(?:\.\d+)?)$/);
    if (match) {
        const firstNum = parseFloat(match[1]);
        const secondNum = parseFloat(match[2]);
        const actualMax = Math.max(firstNum, secondNum);
        const tolerance = actualMax * 0.25;
        if (value < actualMax) return 'normal';
        return (value - actualMax) <= tolerance ? 'borderline' : 'abnormal';
    }

    match = comparisonRange.match(/^[>≥]\s*(\d+(?:\.\d+)?)$/);
    if (match) {
        const min = parseFloat(match[1]);
        const tolerance = min * 0.25;
        if (value > min) return 'normal';
        return (min - value) <= tolerance ? 'borderline' : 'abnormal';
    }

    match = comparisonRange.match(/(\d+(?:\.\d+)?)\s*[-–—]\s*(\d+(?:\.\d+)?)/);
    if (match) {
        const min = parseFloat(match[1]);
        const max = parseFloat(match[2]);
        const rangeSize = max - min;
        const tolerance = rangeSize * 0.25;
        if (value >= min && value <= max) return 'normal';
        if (value < min) return (min - value) <= tolerance ? 'borderline' : 'abnormal';
        if (value > max) return (value - max) <= tolerance ? 'borderline' : 'abnormal';
    }

    return 'normal';
  }

  // ADD THIS HELPER METHOD AND MAKE IT PRIVATE
  private getComparisonReferenceRange(item: HealthMarker): string | null {
    const ocrRange = item.reference_range || '';
    if (!ocrRange || ocrRange.trim() === '') {
      return null;
    }
    const cleanedRange = ocrRange.replace(/\$/g, '').replace(/\\[a-zA-Z]+/g, '').replace(/[{}]/g, '').trim();
    if (!cleanedRange || cleanedRange.trim() === '') {
      return null;
    }
    return cleanedRange.trim();
  }
}
```

**Step 2.2: Simplify the Component**

Open the file `src/app/components/data-table/data-table.component.ts`

Now, replace the complex logic in the component with a simple call to the service.

1.  **DELETE** the entire `getValueStatus` method from `data-table.component.ts`.
2.  **DELETE** the entire `getComparisonReferenceRange` method from `data-table.component.ts`.
3.  **ADD** the new, simplified `getValueStatus` method:
    ```typescript
    // src/app/components/data-table/data-table.component.ts
    
    // ... inside the DataTableComponent class ...
    
    /**
     * Determine Value Status - Delegated to Service
     * 
     * The component now delegates the complex clinical logic to the LabMarkerInfoService.
     * This keeps the component clean and focused on presentation.
     * 
     * @param item - Health marker data
     * @returns Status: 'normal' | 'borderline' | 'abnormal'
     */
    getValueStatus(item: HealthMarker): 'normal' | 'borderline' | 'abnormal' {
      return this.labMarkerService.getMarkerClinicalStatus(item);
    }
    ```
    *(Note: The `labMarkerService` is already injected using `inject()`, so no other changes are needed)*

**D. Verification:**
1.  Run the application.
2.  Navigate to an analysis page that has a data table.
3.  The highlighting of out-of-range values (yellow and red rows/badges) should work exactly as before. The visual behavior is unchanged, but the underlying code is now much cleaner and more robust.

---

### **Quick Win 3: Improve Backend Configuration and Security**

**A. The Goal:**
To stop hard-coding configuration values (like CORS origins) in the Python code and instead load them from environment variables, following industry best practices.

**B. The "Why":**
*   **12-Factor App Principles:** This change follows the standard practice of storing configuration in the environment, separating it from the code. This is a hallmark of a professional, deployable application.
*   **Flexibility:** You can deploy the exact same code to development, staging, and production simply by changing the environment variables. No code changes are needed.
*   **Security:** It prevents sensitive or environment-specific information (like allowed domains) from being checked into version control.

**C. Step-by-Step Implementation:**

**Step 3.1: Update the Settings Model**

Open the file `backend/config/settings.py`

Modify the `Settings` class to include `CORS_ORIGINS`. Pydantic will automatically parse a comma-separated string from the `.env` file into a Python list.

```python
# backend/config/settings.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List # <-- ADD THIS IMPORT

class Settings(BaseSettings):
    """Application settings for the IBA MVP (Cloud-First Deployment)."""
    MISTRAL_API_KEY: str
    CHUTES_AI_API_KEY: str
    SUPABASE_URL: str
    SUPABASE_KEY: str
    SUPABASE_BUCKET_NAME: str = "health-docs"
    
    # ADD THIS LINE
    CORS_ORIGINS: List[str] = ["http://localhost:4200"] 
    
    CHUTES_AI_ENDPOINT: str = "https://llm.chutes.ai/v1"
    CHUTES_AI_MODEL: str = "chutesai/Mistral-Small-3.2-24B-Instruct-2506"
    MISTRAL_OCR_MODEL: str = "mistral-ocr-latest"
    UPLOAD_DIR: str = "uploads"
    model_config = SettingsConfigDict(env_file=".env", extra='ignore')

settings = Settings()
```

**Step 3.2: Update the `.env.example` file**

Open the file `backend/.env.example`

Add the `CORS_ORIGINS` variable so other developers know it's a required setting.

```ini
# backend/.env.example
# ... other variables

# Add or update this line
CORS_ORIGINS=["http://localhost:4200","http://localhost:3000"]
```
*Note: When you create your actual `.env` file, you can put your production domain here as well, e.g., `CORS_ORIGINS=["http://localhost:4200","https://www.my-production-app.com"]`*

**Step 3.3: Use the Setting in the FastAPI App**

Open the file `backend/main.py`

Modify the `CORSMiddleware` to read the origins from your `settings` object.

```python
# backend/main.py
# ... other imports
from services.document_processor import DocumentProcessor
from config.settings import settings # <-- MAKE SURE THIS IS IMPORTED

# ... lifespan function ...

app = FastAPI(
    # ...
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    # REPLACE the hard-coded list with the settings variable
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ... rest of the file ...
```

Excellent idea! Adding a PDF viewer is a fantastic feature that directly addresses both the "switch views" and "debugging" aspects you mentioned. It enhances the application's utility immensely by allowing for direct comparison between the source document and the AI's extracted results. This is a feature a R&D Manager would appreciate as it closes the loop on data verification.

We will implement this as a third view in the `AnalysisComponent`, alongside "Lab Data" and "Medical Insights".

Here is the detailed, step-by-step plan.

---

### **Quick Win 4: Add an Integrated PDF Viewer for Verification and Debugging**

**A. The Goal:**
To embed the original PDF document directly within the analysis page. This will create a three-tab view:
1.  **Lab Data:** The structured table.
2.  **Medical Insights:** The AI-generated report.
3.  **Source Document:** The original, interactive PDF file.

**B. The "Why":**
*   **User Trust and Transparency:** It allows the user to instantly verify the AI's extraction accuracy. If they see a strange result, they can check the source document with one click, building confidence in the tool.
*   **Powerful Debugging Tool:** For developers, this is an invaluable debugging feature. When an AI agent fails to extract a value correctly, you can immediately see the source PDF to understand *why* (e.g., poor OCR quality, complex table structure, unusual wording).
*   **Completes the Analysis Loop:** It provides the full context of the analysis workflow: Source -> Extracted Data -> Insights, all in one unified interface.
*   **Professional Polish:** This feature elevates the application from a simple data display to a comprehensive analysis tool.

**C. Step-by-Step Implementation:**

**Step 4.1: Install the PDF Viewer Library**

We'll use `ngx-extended-pdf-viewer`, a powerful and well-maintained library for Angular.

1.  Open your terminal in the root directory of the project.
2.  Run the following command:
    ```bash
    npm install ngx-extended-pdf-viewer
    ```

**Step 4.2: Configure Angular to Use the Library's Assets**

The library needs to copy its own assets (like the viewer's JavaScript and CSS files) into your application's build output.

1.  Open the file `angular.json`.
2.  Find the `build` -> `options` -> `assets` array.
3.  Add a new entry to this array to include the library's assets.

    ```json
    // in angular.json
    "architect": {
      "build": {
        "options": {
          "assets": [
            "src/favicon.ico",
            "src/assets",
            { // ADD THIS OBJECT
              "glob": "**/*",
              "input": "node_modules/ngx-extended-pdf-viewer/assets/",
              "output": "/assets/"
            }
          ],
          // ... rest of the options
    ```

**Step 4.3: Update the Analysis Component's Template**

Open the file `src/app/pages/analysis/analysis.component.ts`. We'll modify the template string.

1.  **Add a "Source Document" button** to the view toggle group.
2.  **Add a new view section** that contains the PDF viewer component, which will be shown when `currentView()` is `'source'`.

    *Find the `template` section and make these changes:*

    ```typescript
    // src/app/pages/analysis/analysis.component.ts

    // ... imports ...
    import { NgxExtendedPdfViewerModule } from 'ngx-extended-pdf-viewer'; // <-- ADD THIS IMPORT

    @Component({
      // ...
      imports: [
        // ... other imports
        NgxExtendedPdfViewerModule // <-- ADD THIS TO THE IMPORTS ARRAY
      ],
      template: `
        // ... header content ...
    
        @if (isComplete()) {
          <main class="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
            
            <app-disclaimer-banner></app-disclaimer-banner>
    
            <!-- View Toggle -->
            <div class="mb-8 flex justify-center">
              <div class="inline-flex bg-white rounded-lg border border-gray-200 shadow-sm p-1">
                <button
                  (click)="setView('data')"
                  [ngClass]="{...}"
                  class="..."
                >
                  <svg ...></svg>
                  Lab Data
                </button>
                <button
                  (click)="setView('insights')"
                  [ngClass]="{...}"
                  class="..."
                >
                  <svg ...></svg>
                  Medical Insights
                </button>
                <!-- ADD THE NEW BUTTON -->
                <button
                  (click)="setView('source')"
                  [ngClass]="{
                    'bg-blue-600 text-white shadow-sm': currentView() === 'source',
                    'text-gray-600 hover:text-gray-900 hover:bg-gray-50': currentView() !== 'source'
                  }"
                  class="flex items-center px-4 py-3 text-sm font-medium rounded-md transition-all duration-200 ease-in-out min-w-[140px] justify-center"
                >
                  <svg class="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 21h10a2 2 0 002-2V9.414a1 1 0 00-.293-.707l-5.414-5.414A1 1 0 0012.586 3H7a2 2 0 00-2 2v14a2 2 0 002 2z"/>
                  </svg>
                  Source Document
                </button>
              </div>
            </div>
    
            <!-- Content Views -->
            <div class="space-y-6">
              @if (currentView() === 'data') {
                <app-data-table [data]="extractedData()"></app-data-table>
              }
    
              @if (currentView() === 'insights') {
                <app-ai-insights [insights]="aiInsights()"></app-ai-insights>
              }
    
              <!-- ADD THE PDF VIEWER VIEW -->
              @if (currentView() === 'source') {
                <div class="bg-white shadow-sm rounded-lg border border-gray-200 overflow-hidden">
                  <ngx-extended-pdf-viewer
                    [src]="publicUrl()"
                    [height]="'80vh'"
                    [useBrowserLocale]="true"
                    [showSidebarButton]="false"
                    [showFindButton]="true"
                    [showPagingButtons]="true"
                    [showZoomButtons]="true"
                    [showPresentationModeButton]="false"
                    [showOpenFileButton]="false"
                    [showPrintButton]="false"
                    [showDownloadButton]="false"
                    [showBookmarkButton]="false"
                    [showSecondaryToolbarButton]="true"
                    [showRotateButton]="true"
                    [showHandToolButton]="true"
                    [showScrollingButton]="true"
                    [showSpreadButton]="true"
                    >
                  </ngx-extended-pdf-viewer>
                </div>
              }
            </div>
    
            // ... Raw Data Section ...
          </main>
        }
      `
    })
    export class AnalysisComponent implements OnInit, OnDestroy {
      // ...
    ```

**Step 4.4: Update the Analysis Component's Logic**

Now, we need to update the component's code to handle the new view state and provide the PDF URL.

Open the file `src/app/pages/analysis/analysis.component.ts`.

1.  **Update the `currentView` signal** to include `'source'` as a possible value.
2.  **Add a new computed signal** to safely get the document's public URL.

    ```typescript
    // src/app/pages/analysis/analysis.component.ts

    // ...
    export class AnalysisComponent implements OnInit, OnDestroy {
      // ... document signal ...
      readonly showRawData = signal<boolean>(false);
      // UPDATE THIS LINE
      readonly currentView = signal<'data' | 'insights' | 'source'>('data');

      // ... other computed signals ...
      
      // ADD THIS NEW COMPUTED SIGNAL
      readonly publicUrl = computed(() => {
        const doc = this.document();
        // The public_url should come from the document data fetched from the API
        return doc?.public_url || ''; 
      });

      // ... constructor, ngOnInit, ngOnDestroy ...
      
      // UPDATE THE setView METHOD
      setView(view: 'data' | 'insights' | 'source'): void {
        this.currentView.set(view);
      }
      // ...
    }
    ```

**Step 4.5: Ensure the Public URL is Available on the Frontend Model**

The backend provides the `public_url`, but we need to make sure our frontend models and services map it correctly.

1.  Open `src/app/models/document.model.ts`.
2.  Add `public_url` to the `HealthDocument` and `AnalysisResultResponse` interfaces.
3.  Add a `public_url` getter to the `DocumentViewModel`.

    ```typescript
    // src/app/models/document.model.ts

    export interface HealthDocument {
      // ... other properties
      readonly public_url?: string; // <-- ADD THIS
      readonly progress?: number;
      // ...
    }

    export class DocumentViewModel {
      constructor(private document: HealthDocument) {}
      // ... other getters
      get public_url(): string | undefined { return this.document.public_url; } // <-- ADD THIS
      get progress(): number | undefined { return this.document.progress; }
      // ...
    }

    export interface AnalysisResultResponse {
      // ... other properties
      readonly public_url?: string; // <-- ADD THIS
      readonly error_message?: string;
      // ...
    }
    ```

4.  Open `src/app/services/document-analysis.service.ts`.
5.  In the `getAnalysisResults` method, ensure `public_url` is mapped to the store object.

    ```typescript
    // src/app/services/document-analysis.service.ts
    getAnalysisResults(documentId: string): Observable<AnalysisResultResponse> {
        // ...
        const documentForStore: HealthDocument = {
            id: analysis.document_id,
            filename: analysis.filename,
            uploaded_at: analysis.uploaded_at,
            status: analysis.status,
            public_url: analysis.public_url, // <-- ADD THIS MAPPING
            // ... rest of the properties
        };
        // ...
    }
    ```

**D. Verification:**

1.  **Restart the Application:** Run `docker-compose down && docker-compose up --build`.
2.  **View an Analysis:** Navigate to an analysis page that previously had the rendering bug (like the one in your screenshot).
3.  **Check the "UNIT" Column:**
    *   The unit for **Potassium** and **Bicarbonate** should now render cleanly as "mmol/L".
    *   The unit for **Globules rouges** should render cleanly as "/μL".
    *   The `MathFormulaComponent` is now robust enough to handle the variety of inputs, and the improved AI prompt will ensure future extractions are cleaner and more consistent.

This two-part solution makes your application significantly more professional and resilient. You've fixed the bug at the presentation layer and simultaneously hardened the data source, which is an excellent, comprehensive approach.
---

### **Quick Win 5: Create a Resilient LaTeX Rendering System**

You've found an excellent and subtle bug! This is a perfect example of the challenges that arise at the intersection of AI-generated content, data processing, and frontend rendering. The garbled `math..mmol/math..L` is a classic sign that our LaTeX rendering isn't as "resilient and robust" as it needs to be.

You are correct to focus on this. A polished UI is critical, and this rendering issue detracts from the professional look of the data table. Let's fix it properly.

The problem has two layers:
1.  **The Frontend:** The `<app-math-formula>` component is not correctly handling the strings it receives for units. It's too simplistic and fails when it sees LaTeX commands without the expected delimiters.
2.  **The Backend (Potentially):** The AI agent might be inconsistent in how it formats units, sometimes sending plain text (`mg/dL`), sometimes sending LaTeX (`\mu L`), and sometimes sending more complex structures (`\mathrm{mmol/L}`).

We will address both to create a truly robust solution.

---

### **Plan: Create a Resilient LaTeX Rendering System**

**A. The Goal:**
1.  Fix the immediate bug by overhauling the `MathFormulaComponent` to intelligently handle various string formats.
2.  Proactively improve the AI agent's prompt to encourage more consistent and cleaner unit formatting, reducing the likelihood of future errors.

**B. The "Why":**
*   **Data Integrity and Readability:** The user must be able to trust and read the data presented. Garbled units are confusing and unprofessional.
*   **Robustness:** By making the frontend component smarter, we make the entire system more resilient to small variations in the AI's output. We can't always control the AI, but we can control how we render its output.
*   **Reduced Future Bugs:** Improving the AI prompt at the source will prevent this class of error from recurring with other, more complex units in the future.

---

### **Part 1: The Frontend Fix - Overhauling the `MathFormulaComponent`**

This is the most critical part. We will make the component intelligent enough to format the unit string correctly, no matter what it receives.

**File to Edit:** `src/app/components/math-formula/math-formula.component.ts`

**The Current Problem:** The component's logic is too basic. It simply strips `$` signs and tries to render, which fails on complex or non-delimited LaTeX.

**The New Logic:**
1.  Create a `normalizeLatexString` helper method.
2.  This method will inspect the input string and ensure it's perfectly formatted before giving it to the KaTeX rendering engine.
3.  It will handle three cases:
    *   The string is already valid LaTeX (e.g., `$/\mu L$`).
    *   The string is plain text but contains characters that need LaTeX (e.g., `^`, `\`). It will wrap them in `$`.
    *   The string is simple plain text (`mg/dL`) and can be displayed as-is without LaTeX.

**Step 1.1: Replace the contents of `math-formula.component.ts`**

Replace the entire content of the file with this new, more robust implementation.

```typescript
// src/app/components/math-formula/math-formula.component.ts

import { 
  Component, 
  input, 
  viewChild, 
  effect, 
  ChangeDetectionStrategy, 
  ElementRef 
} from '@angular/core';
import * as katex from 'katex';

@Component({
  selector: 'app-math-formula',
  standalone: true,
  template: `<span #container class="math-formula"></span>`,
  styles: [`
    :host { display: inline-block; line-height: 1; }
    .math-formula.error { color: #dc2626; font-family: monospace; }
  `],
  changeDetection: ChangeDetectionStrategy.OnPush,
})
export class MathFormulaComponent {
  readonly expression = input('', {
    transform: (value: string | undefined | null) => value?.trim() || ''
  });

  private readonly container = viewChild.required<ElementRef<HTMLSpanElement>>('container');

  constructor() {
    effect(() => this.renderExpression());
  }

  private renderExpression(): void {
    const element = this.container().nativeElement;
    const rawExpression = this.expression();
    element.classList.remove('error');

    if (!rawExpression) {
      element.innerHTML = '';
      return;
    }

    // NEW: Intelligent normalization logic
    const { normalized, requiresLatex } = this.normalizeLatexString(rawExpression);

    if (requiresLatex) {
      try {
        katex.render(normalized, element, {
          throwOnError: false,
          displayMode: false,
          strict: false,
        });
      } catch (error) {
        console.warn('KaTeX rendering failed, falling back to plain text:', { rawExpression, error });
        element.textContent = rawExpression;
        element.classList.add('error');
      }
    } else {
      // If no LaTeX is needed, just render as plain text.
      element.textContent = normalized;
    }
  }

  /**
   * Normalizes an input string to be safely rendered by KaTeX.
   * - Ensures proper LaTeX delimiters ($...$).
   * - Decides if LaTeX rendering is even necessary.
   */
  private normalizeLatexString(expr: string): { normalized: string; requiresLatex: boolean } {
    if (!expr) {
      return { normalized: '', requiresLatex: false };
    }
    
    // Remove "mathrm" commands from AI, as they are often unnecessary and can cause issues.
    let cleanedExpr = expr.replace(/\\mathrm/g, '').replace(/[{}]/g, '');

    // Check if the expression contains characters that require LaTeX rendering.
    const latexChars = ['\\', '^', '_'];
    const needsLatex = latexChars.some(char => cleanedExpr.includes(char));

    if (!needsLatex) {
      // It's likely plain text, return as is.
      return { normalized: cleanedExpr, requiresLatex: false };
    }

    // It needs LaTeX, so ensure it is properly delimited.
    // Strip any existing dollars to prevent double-wrapping, then wrap it cleanly.
    cleanedExpr = cleanedExpr.replace(/\$/g, '');
    
    return {
      normalized: cleanedExpr, // Give KaTeX the pure expression without delimiters
      requiresLatex: true
    };
  }
}
```

### **Part 2: The Backend Fix - Improving the AI Prompt**

Now, let's guide the AI to give us cleaner data in the first place. This makes our robust frontend a safety net, not a requirement for every single response.

**File to Edit:** `backend/services/extraction_agent.py`

**The Plan:** Add a new section to the system prompt with explicit rules and examples for unit formatting.

**Step 2.1: Update the `system_prompt` in `ExtractionAgent`**

```python
# backend/services/extraction_agent.py

# ... inside the ExtractionAgent class, in the extract_data method ...

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
        3.  **Clean Malformed OCR:** Fix common OCR errors. For example: "<6 - 6.0" should become "<6.0".

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
```

### **Verification**

1.  **Restart the Application:** Run `docker-compose down && docker-compose up --build`.
2.  **View an Analysis:** Navigate to an analysis page that previously had the rendering bug (like the one in your screenshot).
3.  **Check the "UNIT" Column:**
    *   The unit for **Potassium** and **Bicarbonate** should now render cleanly as "mmol/L".
    *   The unit for **Globules rouges** should render cleanly as "/μL".
    *   The `MathFormulaComponent` is now robust enough to handle the variety of inputs, and the improved AI prompt will ensure future extractions are cleaner and more consistent.

This two-part solution makes your application significantly more professional and resilient. You've fixed the bug at the presentation layer and simultaneously hardened the data source, which is an excellent, comprehensive approach.