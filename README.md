# Lab Insight Engine

[![GitHub](https://img.shields.io/badge/GitHub-Repository-blue?logo=github)](https://github.com/ggustin93/agentic-lab-analyzer)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue?logo=docker)](docker-compose.yml)

An AI-powered platform for analyzing medical lab documents, built to demonstrate modern full-stack development practices. This application provides document upload, OCR processing, intelligent analysis, and structured results through a responsive Angular frontend.

## 🚀 Key Features

- **Intelligent Document Processing**: Upload lab reports (PDF, PNG, JPG) and receive structured data extraction with AI-powered insights
- **Agent-Based Architecture**: Modular system with specialized AI agents for OCR and lab data analysis
- **Real-Time Processing**: Monitor document processing status via Server-Sent Events (SSE)
- **Persistent Storage**: Automatic saving of documents and analysis results for future reference
- **Responsive UI**: Clean, modern interface built with Angular 19 and Tailwind CSS

## 🏗️ Architecture

The system employs a decoupled architecture with three main components:

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

### Backend Design Patterns

- **Protocol-Based Agents**: OCR and analysis services implement common interfaces for easy swapping
- **Orchestrator Pattern**: `DocumentProcessor` coordinates workflow while remaining decoupled from specific implementations
- **Secure Configuration**: Environment-based secrets management with Pydantic
- **Versioned API**: Clear `/api/v1/` structure for future extensibility

### Frontend Design Patterns

- **Smart Service/Presentational Components**: Business logic in services, display logic in components
- **RxJS State Management**: Reactive data flow without heavy state libraries
- **OnPush Change Detection**: Optimized rendering cycles
- **Lazy Loading**: Improved initial load performance

## 🔄 Implementation Status

| Component | Current (MVP) | Future Considerations | Status |
|-----------|---------------|----------------------|--------|
| OCR Engine | Mistral AI | docTR (local ML) | Functional |
| Analysis Engine | Chutes.AI | Ollama (local LLM) | Functional |
| Storage | Supabase Cloud | Self-hosted Supabase | Functional |
| Updates | SSE | WebSockets | Functional |

## ⚙️ Tech Stack

- **Frontend**: Angular 19, TypeScript, RxJS, Tailwind CSS
- **Backend**: Python 3.11, FastAPI, Pydantic
- **Database & Storage**: Supabase (PostgreSQL)
- **AI Services**: Mistral AI (OCR), Chutes.AI (Analysis)
- **DevOps**: Docker, Docker Compose, GitHub Actions

## ⚠️ Development Notice

> **Note**: This is a showcase/development application. The current Supabase configuration uses a public bucket for simplicity. Production deployment would require implementing Row Level Security (RLS) and proper authentication mechanisms.

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

## ✅ Testing Strategy

This project follows a pragmatic, risk-based testing strategy focused on ensuring the reliability of core user journeys and complex logic. The current test suite provides high confidence for the MVP while maintaining development velocity.

### Current Test Coverage

1. **Core Service Logic (Unit Test):** The `DocumentAnalysisService` is tested to verify the complete document lifecycle: upload, state updates from mock SSE events, and deletion. This ensures our state management is robust.
2. **Complex UI Logic (Component Test):** The `DataTableComponent` is tested to confirm that its critical out-of-range value highlighting applies the correct CSS classes based on input data.
3. **End-to-End Happy Path (E2E Test):** A Cypress test simulates a user uploading a document and viewing the results, using mocked API calls to ensure the components, services, and routing are correctly wired together.

### Running Tests

**🐋 Docker-Based Testing (Recommended):**
```bash
# Run all tests in Docker
npm run test:all:docker

# Run unit tests only
npm run test:docker

# Run E2E tests only  
npm run e2e:docker

# Run with coverage
npm run test:coverage
```

**🧪 Local Testing:**
```bash
# Run unit tests locally
npm test

# Open Cypress Test Runner
npm run e2e:open
```

**📊 Current Results:**
- ✅ **9/9 Unit Tests Passing** (DocumentAnalysisService + DataTableComponent)
- ✅ **Docker E2E Infrastructure** (Cypress running in containerized environment)  
- ✅ **Critical Happy Path Coverage** (Upload flow + Empty state handling)

## 🔄 CI/CD Pipeline

This project uses GitHub Actions for Continuous Integration, designed to validate code quality and stability on every push and pull request.

### Frontend-Focused CI Strategy

As this project showcases frontend expertise, the CI pipeline is configured to run comprehensive checks exclusively for the Angular application, demonstrating both technical excellence and strategic focus.

The active `frontend-checks` job validates:
- **Code Style:** Ensures all code adheres to the project's linting rules using ESLint
- **Unit & Component Tests:** Executes the full test suite in a headless browser to catch regressions in logic and UI components
- **Production Build:** Compiles the application for production, which validates syntax correctness and dependency configuration

### Full-Stack Awareness

The workflow file (`.github/workflows/ci.yml`) also contains a **disabled `backend-checks` job**. This demonstrates understanding of full-stack CI structure while maintaining focus on frontend expertise. In a production environment, this job would be enabled to run `pytest` for the Python backend, using GitHub Secrets for secure API key management.

### Future CI/CD Enhancements

For production deployment, the pipeline could be extended with:
- **Automated Deployment:** Deploy to staging/production environments
- **Docker Image Building:** Build and push container images to registry
- **Security Scanning:** Dependency vulnerability checks and SAST analysis
- **Performance Testing:** Lighthouse CI for performance regression detection

## 🛣️ Future Enhancements

For production deployment, this application could be enhanced with:

- **Enhanced Security**: Row Level Security (RLS) and user authentication
- **Local Processing**: Local ML/LLM alternatives for data privacy
- **Advanced Communication**: WebSocket integration for bidirectional updates
- **Monitoring**: Application performance and health monitoring
- **Multi-Tenancy**: Support for multiple users with data isolation

## 📖 Development Notes

This project demonstrates modern Angular development patterns including:
- Signal-based state management (Angular 19)
- OnPush change detection optimization
- Comprehensive testing strategy (unit, component, E2E)
- Docker-based development environment
- Professional CI/CD practices

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.