# Lab Insight Engine

[![GitHub](https://img.shields.io/badge/GitHub-Repository-blue?logo=github)](https://github.com/ggustin93/agentic-lab-analyzer)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue?logo=docker)](docker-compose.yml)

A modern, agent-based platform for analyzing medical lab documents with AI-powered insights. This full-stack application provides secure document uploads, performs OCR and intelligent analysis, and delivers structured results through a responsive frontend.

## 🚀 Key Features

- **Intelligent Document Processing**: Upload lab reports (PDF, PNG, JPG) and receive structured data extraction with AI-powered insights.
- **Multi-Agent Architecture**: A robust pipeline with specialized agents for OCR, data extraction, and clinical analysis, ensuring accuracy and maintainability.
- **Reliable, Structured Analysis**: A deterministic analysis layer written in pure Python guarantees accurate range-checking for lab values.
- **Real-Time Processing**: Monitor document processing status via Server-Sent Events (SSE).
- **Persistent Storage**: Automatic saving of documents and analysis results for future reference.
- **Responsive UI**: Clean, modern interface built with Angular 19 and Tailwind CSS.

## 🏗️ Architecture

The system employs a decoupled, multi-agent architecture:

```mermaid
graph TD
    subgraph Frontend
        A[Angular 19 UI]
    end

    subgraph Backend
        B[FastAPI Server]
        C[DocumentProcessor Orchestrator]
        D[Agent 1: MistralOCRService]
        E[Agent 2: LabDataExtractorAgent]
        F[Agent 3: ClinicalInsightAgent]
    end

    subgraph Platform
        G[Supabase Storage & DB]
    end

    A -- Uploads --> B
    B -- Triggers --> C
    C -- Manages --> D
    D -- text --> C
    C -- text --> E
    E -- analyzed_data --> C
    C -- analyzed_data --> F
    F -- final_insights --> C
    C -- Stores in --> G
    A -- Streams status from --> B
```

### Backend Design Patterns

- **Multi-Agent Pipeline**: Specialized agents handle distinct tasks (OCR, Extraction, Insights) for improved robustness and maintainability.
- **Orchestrator Pattern**: `DocumentProcessor` coordinates the agent workflow while remaining decoupled from specific implementations.
- **Hybrid AI & Deterministic Logic**: Uses AI for complex, unstructured tasks (like text extraction) and pure Python for critical, deterministic tasks (like range checking) to ensure accuracy.
- **Secure Configuration**: Environment-based secrets management with Pydantic.
- **Versioned API**: Clear `/api/v1/` structure for future extensibility

### Frontend Design Patterns

- **Smart Service/Presentational Components**: Business logic in services, display logic in components
- **RxJS State Management**: Reactive data flow without heavy state libraries
- **OnPush Change Detection**: Optimized rendering cycles
- **Lazy Loading**: Improved initial load performance

## 🔄 Current Implementation vs. Future Roadmap

| Component | Current (MVP) | Planned Evolution | Status |
|-----------|---------------|-------------------|--------|
| OCR Engine | Mistral AI | docTR (local ML) | In Development |
| Analysis Engine | Chutes.AI | Ollama (local LLM) | Planned |
| Storage | Supabase Cloud | Self-hosted Supabase | Planned |
| Updates | SSE | WebSockets | Planned |

## ⚙️ Tech Stack

- **Frontend**: Angular 19, TypeScript, RxJS, Tailwind CSS
- **Backend**: Python 3.11, FastAPI, Pydantic
- **Database & Storage**: Supabase (PostgreSQL)
- **AI Services**: Mistral AI (OCR), Chutes.AI (Extraction & Analysis)
- **DevOps**: Docker, Docker Compose, GitHub Actions

## ⚠️ Security Notice: MVP Configuration

> **Note**: The current security configuration is for MVP development purposes only. The Supabase bucket is public and Row Level Security (RLS) is not yet enabled. This is a known issue tracked for resolution before production deployment.

## 🚀 Getting Started

### Prerequisites

- Docker & Docker Compose
- Supabase account
- API keys for Mistral AI and Chutes.AI

### Quick Setup

1. **Set up Supabase**
   - Create a new Supabase project
   - Create a public bucket named `health_documents`
   - Get your Project URL and `service_role` key

2. **Configure Environment**
   ```bash
   # backend/.env
   SUPABASE_URL="your_project_url"
   SUPABASE_KEY="your_service_role_key"
   MISTRAL_API_KEY="your_mistral_api_key"
   CHUTES_AI_API_KEY="your_chutes_ai_key"
   ```

3. **Launch the Application**
   ```bash
   docker-compose up --build
   ```
   
   Access the frontend at `http://localhost:4200` and the API at `http://localhost:8000`

## 🛣️ Roadmap

- **Local-First Processing**: Complete local ML/LLM alternatives for privacy-focused deployment
- **Enhanced Security**: Enable RLS and implement proper authentication
- **WebSocket Communication**: Replace SSE with bidirectional WebSockets
- **Application Monitoring**: Add Prometheus/Grafana integration
- **Multi-Tenant Support**: Enable multi-user functionality with proper isolation

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.