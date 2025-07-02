# AI-Powered Health Document Analyzer

This project is a full-stack application designed to analyze health documents using a modern, agent-based architecture. The system provides secure document uploads, performs OCR and AI-driven analysis, and delivers results to a responsive frontend via real-time streaming. Documents and analysis data are persisted using Supabase.

## ⚠️ Security Notice: MVP Configuration
> **Note**: The current security configuration is for MVP development purposes only. The Supabase bucket is public and Row Level Security (RLS) is not yet enabled on the database tables. This is a known issue tracked for resolution before any production deployment. Implementing proper authentication and authorization policies is a critical next step.

## Core Features

*   **Secure Document Upload**: Handles PDF, PNG, and JPG files, with storage managed by Supabase.
*   **Hybrid Processing**: Currently uses cloud-based services (Mistral OCR, Chutes.AI) with a roadmap for fully local alternatives.
*   **Persistent Storage**: Uses Supabase Cloud for PostgreSQL database and file storage.
*   **Agent-Based Backend**: Orchestrates specialized AI agents for OCR and insight extraction.
*   **Real-Time Updates**: Uses Server-Sent Events (SSE) to stream analysis progress.
*   **Containerized Environment**: Fully dockerized for simple, one-command setup and deployment.
*   **CI/CD Ready**: Includes a GitHub Actions workflow for automated checks.

## Architecture Overview

The system employs a decoupled architecture. The FastAPI backend serves a versioned REST API and communicates with the Supabase platform for data and file persistence.

```
┌───────────────────────┐      ┌───────────────────────────┐      ┌─────────────────────────┐
│   Angular 19 Frontend │      │      FastAPI Backend      │      │     Supabase Platform     │
│ (OnPush, Async Pipe)  ├─────►│      (Agent-Based)        ├─────►│  (Postgres & Storage)   │
├───────────────────────┤      ├───────────────────────────┤      ├─────────────────────────┤
│ - Document Upload     │      │  POST /api/v1/docs/upload │      │ - User Documents        │
│ - Real-Time View      │◄─────┤───────────────────────────┤      │ - Analysis Results      │
│   (via EventSource)   │      │  GET  /api/v1/docs/:id/stream (SSE) │      │ - File Storage Bucket   │
└───────────────────────┘      ├───────────────────────────┤      └─────────────────────────┘
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

## Current Implementation vs. Future Roadmap

### Current MVP Implementation

The current MVP uses a hybrid approach with the following cloud-based components:

| Component | Current Implementation | Processing Location |
|-----------|------------------------|---------------------|
| OCR Engine | Mistral AI | Cloud API |
| Analysis Engine | Chutes.AI with Mistral | Decentralized Cloud |
| Database & Storage | Supabase Cloud | Cloud Service |

### Roadmap: Local-First Architecture

A key goal of this project is to transition to a fully local-first architecture:

| Component | Current | Planned Local Alternative | Status |
|-----------|---------|---------------------------|--------|
| OCR Engine | Mistral AI | docTR (local ML model) | In Development |
| Analysis Engine | Chutes.AI | Ollama (local LLM) | Planned |
| Database & Storage | Supabase Cloud | Self-hosted Supabase | Planned |

The application will include a settings interface to toggle between cloud and local processing options, allowing users to prioritize either performance or privacy according to their needs.

## Tech Stack

*   **Frontend**: Angular 19, TypeScript, RxJS, Tailwind CSS
*   **Backend**: Python 3.11, FastAPI, Pydantic
*   **Database & Storage**: Supabase (PostgreSQL, Supabase Storage)
*   **AI Services**: 
    * Current: Mistral AI (OCR), Chutes.AI (Insights)
    * Planned: docTR (local OCR), Ollama (local LLM)
*   **Tooling**: Docker, Docker Compose, GitHub Actions

## Local Development

### Prerequisites
*   Docker & Docker Compose
*   A Supabase account
*   API keys for Mistral AI and Chutes.AI (required for current implementation)

### 1. Set up Supabase
1.  Create a new project on [Supabase](https://app.supabase.com/).
2.  Inside your project, go to the **Storage** section and create a new **public bucket** named `health_documents`.
3.  Go to the **Project Settings -> API** section and get your Project URL and `service_role` key.

### 2. Configure Environment

Create a `.env` file in the `backend/` directory with your Supabase credentials:

```dotenv
# backend/.env

# Supabase Credentials
SUPABASE_URL="your_project_url"
SUPABASE_KEY="your_service_role_key" # Important: Use the service_role key for backend operations

# AI Services (required for current implementation)
MISTRAL_API_KEY="your_mistral_api_key"
CHUTES_AI_API_KEY="your_chutes_ai_key"
```

### 3. Run the Application

From the project root, start the services:

```bash
docker-compose up --build
```
The frontend is available at `http://localhost:4200`, and the backend API is exposed on `http://localhost:8000`.

## Next Steps

Future development will focus on enhancing modularity, privacy, and observability:

*   **Local AI Agents**: Complete implementation of agents that use local models (docTR, Ollama) for offline capability.
*   **Settings Interface**: Add UI for toggling between cloud and local processing options.
*   **Self-hosted Supabase**: Add support for connecting to a self-hosted Supabase instance.
*   **WebSocket Communication**: Transition from SSE to WebSockets to enable features like task cancellation.
*   **Application Monitoring**: Integrate tools like Prometheus and Grafana for performance monitoring.