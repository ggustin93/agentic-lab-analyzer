# AI-Powered Health Document Analyzer

This project is a full-stack application designed to analyze health documents using a modern, agent-based architecture. The system provides secure document uploads, performs OCR and AI-driven analysis, and delivers results to a responsive frontend via real-time streaming.

## Core Features

*   **Secure Document Upload**: Handles PDF, PNG, and JPG files.
*   **Agent-Based Backend**: Orchestrates specialized AI agents for OCR and insight extraction.
*   **Real-Time Updates**: Uses Server-Sent Events (SSE) to stream analysis progress.
*   **Containerized Environment**: Fully dockerized for simple, one-command setup and deployment.
*   **CI/CD Ready**: Includes a GitHub Actions workflow for automated checks.

## Architecture Overview

The system employs a decoupled architecture with a versioned REST API separating the frontend and backend.

```
┌───────────────────────┐      ┌───────────────────────────┐
│   Angular 19 Frontend │      │      FastAPI Backend      │
│ (OnPush, Async Pipe)  │      │      (Agent-Based)        │
├───────────────────────┤      ├───────────────────────────┤
│ - Document Upload     │      │  POST /api/v1/docs/upload │
│ - Real-Time View      │◄─────┼───────────────────────────┤
│   (via EventSource)   │      │  GET  /api/v1/docs/:id/stream (SSE)
└───────────────────────┘      ├───────────────────────────┤
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

The backend's `DocumentProcessor` orchestrates two key agents:
1.  **`OCRExtractorAgent`**: A protocol for services that extract text from a document.
2.  **`LabInsightAgent`**: A protocol for services that analyze text to generate structured insights.

This design promotes modularity, testability, and separation of concerns.

## Tech Stack

*   **Frontend**: Angular 19, TypeScript, RxJS, Tailwind CSS
*   **Backend**: Python 3.11, FastAPI, Pydantic
*   **AI Services**: Mistral AI (OCR), Chutes.AI (Insights)
*   **Tooling**: Docker, Docker Compose, GitHub Actions

## Local Development

### Prerequisites
*   Docker & Docker Compose
*   API keys for Mistral AI and Chutes.AI

### 1. Configure Environment

Create a `.env` file in the `backend/` directory:

```dotenv
# backend/.env
MISTRAL_API_KEY="your_mistral_api_key"
CHUTES_AI_API_KEY="your_chutes_ai_key"
```

### 2. Run the Application

From the project root, start the services:

```bash
docker-compose up --build
```
The frontend is available at `http://localhost:4200`, and the backend API is exposed on `http://localhost:8000`.

## Next Steps

Future development will focus on enhancing modularity and observability:

*   **Local AI Agents**: Implement agents that use local models (e.g., `docTR`, `Ollama`) for offline capability.
*   **WebSocket Communication**: Transition from SSE to WebSockets to enable features like task cancellation.
*   **Application Monitoring**: Integrate tools like Prometheus and Grafana for performance monitoring.