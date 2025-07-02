# Lab Analyzer

A full-stack application for analyzing health documents using AI. It features a FastAPI backend with an agent-based architecture and an Angular 20 frontend for data visualization and real-time updates.

## Features

*   Secure document upload (PDF, PNG, JPG).
*   Real-time analysis status updates using Server-Sent Events (SSE).
*   AI-powered text extraction (OCR) and structured insight generation.
*   Clear data visualization for extracted health markers.
*   Containerized for easy setup and deployment with Docker.
*   CI/CD pipeline for automated testing and validation.

## Architecture

The system uses a decoupled frontend/backend architecture communicating via a versioned REST API.

```
┌───────────────────────────┐      ┌───────────────────────────┐
│     Angular 20 Frontend   │      │      FastAPI Backend      │
│ (Performance-Optimized)   │      │      (Agent-Based)        │
├───────────────────────────┤      ├───────────────────────────┤
│ - UploadZone Component    │      │                           │
│ - DocumentList (OnPush)   │      │  /api/v1/documents/upload │
│ - DataTable (OnPush)      │◄─────┼───────────────────────────┤
│ - SSE Service for Real-   │      │                           │
│   Time Updates            │      │  /api/v1/documents/:id/stream (SSE)
└───────────────────────────┘      ├───────────────────────────┤
                                   │                           │
                                   │      DocumentProcessor    │
                                   │     (Orchestrator)        │
                                   ├─────────────┬─────────────┤
                                   │             │             │
                                   ▼             ▼             │
                         ┌───────────┐   ┌───────────┐
                         │ OCRExtractor│   │ LabInsight  │
                         │ Agent       │   │ Agent       │
                         └───────────┘   └───────────┘
```

The backend employs an agent-based design where a `DocumentProcessor` orchestrates two specialized agents:
1.  **`OCRExtractorAgent`**: Extracts text from documents.
2.  **`LabInsightAgent`**: Analyzes text and generates structured health insights.

This design promotes separation of concerns, making the system more modular and testable.

## Tech Stack

*   **Frontend**: Angular 19, TypeScript, RxJS, Tailwind CSS
*   **Backend**: Python 3.11, FastAPI, Pydantic
*   **AI Services**: Mistral AI (OCR), Chutes.AI (Insights)
*   **Tooling**: Docker, Docker Compose, GitHub Actions, Ruff, Pytest

## Getting Started

This project is fully containerized for a "one-command" setup.

### Prerequisites
*   Docker and Docker Compose
*   An API key for Mistral AI and Chutes.AI

### 1. Create Environment File

Create a file named `.env` inside the `backend/` directory with your API keys:

```dotenv
# backend/.env
MISTRAL_API_KEY="your_mistral_api_key_here"
CHUTES_AI_API_KEY="your_chutes_ai_api_key_here"
```

### 2. Run with Docker Compose

From the project root, execute:

```bash
docker-compose up --build
```
The application will be available at `http://localhost:4200`.

## API Endpoints (v1)

| Method | Endpoint                             | Description                                            |
|--------|--------------------------------------|--------------------------------------------------------|
| `POST` | `/api/v1/documents/upload`           | Upload a document for analysis.                        |
| `GET`  | `/api/v1/documents/{id}/stream`      | Stream analysis results for a document via SSE.        |
| `GET`  | `/api/v1/documents`                  | Get a list of all documents and their status.          |

## Next Steps

*   **Local Mode**: Implement agent classes that leverage local models (like `docTR` for OCR and Ollama for insights) for a fully offline mode.
*   **WebSockets**: Upgrade from SSE to WebSockets for bi-directional communication, allowing for cancellation of analysis jobs.
*   **Enhanced Monitoring**: Integrate Prometheus and Grafana for detailed application performance monitoring.