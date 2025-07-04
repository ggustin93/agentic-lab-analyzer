# 🚧 [WIP] : DocBot AI: Health Document Analyzer

[![GitHub](https://img.shields.io/badge/GitHub-Repository-blue?logo=github)](https://github.com/ggustin93/agentic-lab-analyzer)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![CI Status](https://github.com/ggustin93/agentic-lab-analyzer/actions/workflows/ci.yml/badge.svg)](https://github.com/ggustin93/agentic-lab-analyzer/actions/workflows/ci.yml)
[![Docker Ready](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker)](docker-compose.yml)
[![Angular](https://img.shields.io/badge/Angular-v19-DD0031?logo=angular)](https://angular.io)
[![Python](https://img.shields.io/badge/Python-v3.11-3776AB?logo=python)](https://www.python.org)

---

> ⚠️ **Important Notice**  
> - This repository is an early-stage proof of concept, initiated in July 2025 as part of job interview preparation.  
> - The codebase is under active development and may contain incomplete features or vulnerabilities.  

---

An AI-powered platform for analyzing medical lab documents, built to demonstrate modern full-stack development practices. This application provides document upload, OCR processing, intelligent analysis, and structured results through a responsive Angular frontend.

An AI-powered platform for analyzing medical lab documents, built to demonstrate modern full-stack development practices. This application provides document upload, OCR processing, intelligent analysis, and structured results through a responsive Angular frontend.

## 🚀 Key Features

- **Intelligent Document Processing**: Upload lab reports (PDF, PNG, JPG) and receive structured data extraction with AI-powered insights
- **Agent-Based Architecture**: Modular system with specialized AI agents for OCR and lab data analysis
- **Real-Time Processing**: Monitor document processing status via Server-Sent Events (SSE)
- **Persistent Storage**: Automatic saving of documents and analysis results for future reference
- **Responsive UI**: Clean, modern interface built with Angular 19 and Tailwind CSS

## 🏗️ Architecture

The system employs a decoupled, containerized architecture with three main components: a responsive Angular frontend, a Python/FastAPI backend, and the Supabase platform for database and storage.

### High-Level Diagram
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

### Project Structure

```
/
├── .github/workflows/        # CI/CD pipeline configuration
├── backend/                  # Python/FastAPI backend application
│   ├── agents/               # AI agent implementations
│   ├── services/             # Core business logic (e.g., DocumentProcessor)
│   ├── main.py               # FastAPI application entrypoint
│   └── requirements.txt      # Python dependencies
├── src/                      # Angular frontend application
│   ├── app/
│   │   ├── components/       # Reusable UI components
│   │   ├── services/         # Frontend business logic and API communication
│   │   └── pages/            # Main application pages/views
│   ├── index.html            # Main HTML page
│   └── main.ts               # Angular application entrypoint
├── supabase/                 # Supabase schema migrations
│   └── migrations/
├── cypress/                  # End-to-end tests
├── docker-compose.yml        # Docker orchestration for local development
├── Dockerfile.frontend       # Docker build instructions for Angular app
├── Dockerfile                # Docker build instructions for FastAPI app
└── README.md                 # You are here!
```

Understood. The goal is to be technically precise and professional, but with a neutral, objective tone that lets the work speak for itself. This version strips away any enthusiastic or overly descriptive language and presents the design patterns as clean, factual architectural decisions.

Here is the revised, more humble, concise, and professional version.

---

## 🏗️ Architecture & Design Patterns

The application is built on a set of established design patterns chosen for modularity, maintainability, and performance.

### Backend Design

Yes, you absolutely should mention FastAPI.

For a technical audience, especially in a full-stack context, naming the specific backend framework is crucial. FastAPI is not just *any* Python framework; it's a marker of modern, high-performance development.

Here's why mentioning it is a significant advantage:

1.  **Signals Modernity and Performance:** FastAPI is known for being one of the fastest Python web frameworks available. Choosing it shows that you prioritize performance, which is a key concern for any senior engineer.
2.  **Asynchronous by Default:** It's built on `asyncio` from the ground up. Mentioning it immediately communicates that you are comfortable with modern asynchronous programming in Python, a highly valued skill.
3.  **Automatic API Documentation:** FastAPI automatically generates interactive API documentation (like Swagger UI). This demonstrates that you value good developer experience and clear API contracts, which is a very professional trait.
4.  **Pydantic Integration:** It has deep, native integration with Pydantic. Since you're already using Pydantic, mentioning FastAPI shows that you've chosen a cohesive and logical tech stack where the parts work seamlessly together.

### How to Integrate it Naturally

You don't need a whole new section. The best way is to integrate it into the existing `Backend Design` section. Here is the revised section, now including FastAPI. The change is small but adds significant technical weight.

---

### **Revised `Backend Design` Section**

### Backend Design

The Python backend is built with **FastAPI** for its high performance and native asynchronous capabilities. This choice supports a scalable and responsive service, ideal for handling I/O-bound operations like calls to AI APIs. The architecture is guided by the following principles:

-   **Orchestrator Pattern**: A central `DocumentProcessor` service coordinates the multi-step analysis workflow, delegating tasks to specialized agents.
-   **Protocol-Based Agents**: AI services for OCR and analysis implement a common `Protocol` (interface). This allows different AI providers to be used interchangeably without altering the core business logic.
-   **Type-Safe API with Pydantic**: FastAPI's native integration with **Pydantic** is used for robust, automatic request/response validation and to generate clear, interactive API documentation.
-   **Secure Configuration**: All settings and secrets are managed through environment variables, loaded and validated by a Pydantic `BaseSettings` model at startup.


### Frontend Design

The Angular frontend implements modern architectural patterns for maintainability and performance.

-   **Signal-Based State Management**: Uses Angular 19's native signals through a dedicated `DocumentStore` for reactive state management, with `DocumentAnalysisService` handling workflow orchestration.
-   **Separation of Concerns**: Three-layer architecture separating state (`DocumentStore`), business logic (`DocumentAnalysisService`), and HTTP operations (`DocumentApiService`).
-   **Performance Optimization**: `OnPush` change detection with standalone components for optimal rendering and tree-shaking.
-   **Modern Patterns**: `inject()` function for dependency injection, computed signals for derived state, and effect-based side effect management.

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

This project demonstrates modern Angular 19 patterns:
- Three-layer service architecture with signal-based state management
- Separation of state (`DocumentStore`), business logic (`DocumentAnalysisService`), and API calls (`DocumentApiService`)
- Professional documentation and TypeScript typing throughout
- Comprehensive testing strategy covering critical workflows
- Docker-based development environment with CI/CD

## 📝 License

This project is licensed under the MIT License.
