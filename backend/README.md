# Backend - Lab Insight Engine

This directory contains the application's backend, built with Python and FastAPI. It is responsible for handling document uploads, orchestrating the AI agent pipeline for analysis, and persisting data with Supabase.

## API Documentation
Once the API is running, interactive documentation is available via:
- **Swagger UI**: [`http://localhost:8000/docs`](http://localhost:8000/docs)
- **ReDoc**: [`http://localhost:8000/redoc`](http://localhost:8000/redoc)

## Core Endpoints
- `POST /api/v1/docs/upload`: Uploads and processes a new document.
- `GET /api/v1/docs`: Lists all documents and their current status.
- `GET /api/v1/docs/{document_id}`: Retrieves the full analysis for a specific document.
- `GET /api/v1/docs/{document_id}/stream`: Opens a Server-Sent Events (SSE) stream for real-time progress tracking.
- `DELETE /api/v1/docs/{document_id}`: Deletes a document and its associated analysis.

## Architecture: Multi-Agent Pipeline

The backend is built around a robust pipeline of three specialized agents, orchestrated by the `DocumentProcessor`. This design pattern ensures a clean separation of concerns and high maintainability.

1.  **Agent 1: OCR (`MistralOCRService`)**
    -   **Responsibility**: To extract raw text from a document (PDF or image) using the Mistral AI API.
    -   **Output**: A string containing the document's unstructured text.

2.  **Agent 2: Data Extraction & Analysis (`LabDataExtractorAgent`)**
    -   **Responsibility**: This agent performs a hybrid task:
        -   **Extraction (AI)**: It uses a Large Language Model (LLM) to parse the raw text and extract structured data (markers, values, units, reference ranges).
        -   **Analysis (Python)**: It then uses deterministic Python logic to analyze the extracted data, comparing each marker's value against its reference range to determine a severity status (e.g., `normal`, `warning_high`, `danger_low`).
    -   **Output**: An `AnalyzedHealthData` object containing the structured, enriched data.

3.  **Agent 3: Clinical Insight Generation (`ClinicalInsightAgent`)**
    -   **Responsibility**: This agent takes the structured, pre-analyzed data from Agent 2 and uses an LLM to generate a high-level summary, key findings, and lifestyle recommendations in accessible, human-readable language.
    -   **Output**: The final insights that are combined into the `HealthInsights` object.

### Architectural Advantages
- **Accuracy**: By separating tasks, we use the best tool for each job. LLMs handle complex language tasks, while reliable Python code handles critical, deterministic logic.
- **Robustness**: An error in one agent (e.g., insight generation fails) does not compromise the output of previous agents (e.g., the structured data is still saved).
- **Maintainability**: Each agent is a modular component that can be updated, improved, or replaced independently without affecting the rest of the system.

## Key Data Models (`models/health_models.py`)

The data flow is structured around a clear set of Pydantic models:

```python
# The final, analyzed output from the Data Extractor Agent
class AnalyzedHealthData(BaseModel):
    markers: List[AnalyzedHealthMarker]
    document_type: str
    test_date: Optional[str]

# The final, combined output of the entire analysis pipeline,
# structured for the frontend UI.
class HealthInsights(BaseModel):
    data: AnalyzedHealthData
    summary: str
    key_findings: List[str]
    recommendations: List[str]
```

## Core Services

- **`DocumentProcessor`**: The main orchestrator service that manages the pipeline, updates the document's state in the database, and streams progress to the frontend via SSE.
- **`MistralOCRService`**: The implementation of the OCR agent.
- **`LabDataExtractorAgent`**: The implementation of the extraction and analysis agent.
- **`ClinicalInsightAgent`**: The implementation of the insight generation agent.