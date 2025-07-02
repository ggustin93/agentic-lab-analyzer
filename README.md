# AI-Powered Health Document Analyzer

A full-stack application for analyzing health documents using an agent-based architecture. The system handles document uploads, performs OCR and AI-driven analysis, and delivers results via real-time streaming.

[![GitHub](https://img.shields.io/badge/GitHub-Repository-blue?logo=github)](https://github.com/ggustin93/agentic-lab-analyzer)

## ⚠️ Security Notice: MVP Configuration
> **Note**: Current security configuration is for MVP development only. The Supabase bucket is public and Row Level Security (RLS) is not yet enabled. This is a known issue tracked for resolution before production deployment.

## Core Features

*   **Document Processing**: Handles PDF, PNG, and JPG files with Supabase storage
*   **AI Analysis**: Uses cloud-based services (Mistral OCR, Chutes.AI) with planned local alternatives
*   **Agent-Based Architecture**: Specialized AI agents for OCR and insight extraction
*   **Real-Time Updates**: Server-Sent Events (SSE) for streaming analysis progress
*   **Containerized Deployment**: Docker and Docker Compose for simple setup

## Architecture Overview

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
1. **`OCRExtractorAgent`**: Extracts text from documents
2. **`LabInsightAgent`**: Analyzes text to generate structured insights

## Implementation: Current vs. Future

### Current MVP

| Component | Current Implementation | Processing Location |
|-----------|------------------------|---------------------|
| OCR Engine | Mistral AI | Cloud API |
| Analysis Engine | Chutes.AI with Mistral | Cloud |
| Database & Storage | Supabase Cloud | Cloud Service |

### Roadmap: Local-First Architecture

| Component | Current | Planned Local Alternative | Status |
|-----------|---------|---------------------------|--------|
| OCR Engine | Mistral AI | docTR (local ML model) | In Development |
| Analysis Engine | Chutes.AI | Ollama (local LLM) | Planned |
| Database & Storage | Supabase Cloud | Self-hosted Supabase | Planned |

## Tech Stack

*   **Frontend**: Angular 19, TypeScript, RxJS, Tailwind CSS
*   **Backend**: Python 3.11, FastAPI, Pydantic
*   **Database & Storage**: Supabase (PostgreSQL, Storage)
*   **AI Services**: Mistral AI (OCR), Chutes.AI (Insights)
*   **Tooling**: Docker, Docker Compose, GitHub Actions

## Getting Started

### Prerequisites
*   Docker & Docker Compose
*   Supabase account
*   API keys for Mistral AI and Chutes.AI

### Setup

1. **Supabase Configuration**
   ```
   - Create a new project on Supabase
   - Create a public bucket named 'health_documents'
   - Get your Project URL and service_role key
   ```

2. **Environment Setup**
   ```
   # backend/.env
   SUPABASE_URL="your_project_url"
   SUPABASE_KEY="your_service_role_key"
   MISTRAL_API_KEY="your_mistral_api_key"
   CHUTES_AI_API_KEY="your_chutes_ai_key"
   ```

3. **Run Application**
   ```bash
   docker-compose up --build
   ```
   Frontend: http://localhost:4200
   Backend API: http://localhost:8000

## Development Roadmap

*   **Local AI Agents**: Complete implementation of local models (docTR, Ollama)
*   **Settings Interface**: Toggle between cloud and local processing options
*   **Self-hosted Supabase**: Support for connecting to self-hosted instances
*   **WebSocket Communication**: Replace SSE with WebSockets for task cancellation
*   **Application Monitoring**: Integration with Prometheus and Grafana