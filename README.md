# DocBot AI – Health Document Analyzer

> ⚠️ **Important Notice**
>
> This repository is a proof-of-concept, initiated in July 2025 as part of a job interview preparation process. The codebase is under active development and may contain incomplete features or vulnerabilities. It is not intended for production or medical use.

This project is a full-stack application designed to analyze medical lab documents. It demonstrates a modern software architecture using Angular, FastAPI, and an agent-based backend system to process and interpret health data.

## Features

*   **Document Upload & OCR**: Accepts PDF and image files, extracting text using an OCR agent.
*   **Multi-Stage Processing**: An asynchronous backend orchestrates a pipeline for OCR, AI analysis, and data persistence.
*   **Real-Time Feedback**: The user interface provides live status updates on document processing via Server-Sent Events (SSE).
*   **Structured Data Extraction**: An AI agent parses raw text into structured JSON, identifying health markers, values, units, and reference ranges.
*   **AI-Generated Insights**: A second agent generates a human-readable summary, key findings, and general recommendations from the structured data.
*   **Out-of-Range Highlighting**: Lab results automatically highlight values that fall outside their reference range.
*   **Document Management**: Provides a history of all analyses with options to delete documents or retry failed processing jobs.
*   **Containerized Environment**: The entire application stack is containerized using Docker and Docker Compose for easy setup.
*   **Automated Testing & CI/CD**: Includes a multi-layered testing strategy and a GitHub Actions workflow for continuous integration.

## Architecture Overview

The application is built on a decoupled architecture, separating the frontend, backend, and data services.

#### High-Level Diagram
```
┌─────────────────────────┐      ┌───────────────────────────┐      ┌─────────────────────────┐
│   Angular 19 Frontend   │◄───► │      FastAPI Backend      │      │     Supabase Platform   │
│ (Signals, OnPush, SSE)  │      │   (Agent Orchestrator)    │      │  (Postgres & Storage)   │
├─────────────────────────┤      ├───────────────────────────┤      ├─────────────────────────┤
│ - Document Upload       │      │ - DocumentProcessor       │      │ - Document Records      │
│ - Real-Time Dashboard   │      │ - API Endpoints (v1)      │      │ - Analysis Results      │
│ - Analysis Results View │      │ - SSE Stream Endpoint     │      │ - Stored PDF/Image Files│
└─────────────────────────┘      └────────────┬──────────────┘      └─────────────────────────┘
                                              │
                                              ▼
                               ┌───────────────────────────┐
                               │    AI & OCR Services      │
                               │  (Mistral OCR, ChutesAI)  │
                               └───────────────────────────┘
```

#### Frontend (Angular 19)
The frontend is built with Angular 19, utilizing signals for state management, `OnPush` change detection for performance, and a three-tier service architecture to separate concerns (API communication, state management, and business logic).

#### Backend (Python / FastAPI)
The Python backend uses FastAPI for its asynchronous capabilities. It is designed with an agent-based orchestrator pattern, where a `DocumentProcessor` coordinates the workflow between swappable agents responsible for OCR and data analysis. This modular design allows different AI services to be integrated without altering core business logic.

#### Data & Persistence (Supabase)
Supabase provides the PostgreSQL database and file storage. Schema changes are managed through version-controlled SQL migrations located in the `supabase/migrations` directory.

## Tech Stack

| Layer       | Technology                                                              |
|-------------|-------------------------------------------------------------------------|
| **Frontend**  | Angular 19, TypeScript, Tailwind CSS, Signals, RxJS, Cypress, Karma   |
| **Backend**   | Python 3.11, FastAPI, Pydantic, httpx                                   |
| **AI / ML**   | Mistral AI (for OCR), Chutes.AI (for analysis)                          |
| **Database**  | Supabase (PostgreSQL)                                                   |
| **Storage**   | Supabase Storage                                                        |
| **DevOps**    | Docker, Docker Compose, GitHub Actions                                  |

## Testing Strategy
A multi-layered testing strategy is implemented to ensure high confidence in the application's stability, from individual functions to complete user flows.

| Layer | Goal | Tools | Coverage & Examples |
| :--- | :--- | :--- | :--- |
| **Unit & Component Tests** | Validate individual units of code and UI components in isolation. | **Jasmine & Karma** | **Services (`DocumentAnalysisService`):** Testing the core business logic, including the entire document lifecycle (upload, SSE updates, deletion) using `HttpClientTestingModule` for mocking API calls. <br><br> **Components (`DataTableComponent`):** Validating complex UI logic, such as the dynamic CSS class binding for highlighting out-of-range lab values, and testing signal-based inputs. |
| **End-to-End (E2E) Tests** | Validate critical user flows from the user's perspective across the entire frontend application. | **Cypress** | Simulating the full user journey: uploading a file, observing the real-time processing status on the dashboard, and navigating to the final analysis page. The backend is mocked using Cypress intercepts to provide consistent API responses, allowing the frontend to be tested in isolation. |
| **Continuous Integration** | Automate quality assurance and prevent regressions before code is merged. | **GitHub Actions** | On every push to `main`, the CI pipeline automatically runs: <ul><li>Linting (`ESLint`) to enforce code style.</li><li>All unit and component tests.</li><li>A production build check (`ng build`) to catch Ahead-of-Time (AOT) compilation errors.</li></ul> |

#### Running Tests
```bash
# Run Angular unit and component tests
npm test

# Run the complete test suite (unit + E2E) in Docker
npm run test:all:docker

# Open the Cypress UI for interactive E2E testing
npm run e2e:open
```

## Local Development
Follow these steps to run the application on your local machine.

#### Prerequisites
*   Docker & Docker Compose
*   A Supabase account
*   API keys for **Mistral AI** and **Chutes.AI**

#### 1. Configure Environment
Create a `.env` file in the `backend/` directory by copying the example file:
```bash
cp backend/.env.example backend/.env
```
Edit `backend/.env` and add your credentials:
```ini
# backend/.env
MISTRAL_API_KEY=your_mistral_api_key
CHUTES_AI_API_KEY=your_chutes_ai_key
SUPABASE_URL=your_supabase_project_url
SUPABASE_KEY=your_supabase_service_role_key
SUPABASE_BUCKET_NAME=health-docs # or your chosen bucket name
```
*Note: You will also need to set up the database schema using the files in `supabase/migrations`.*

#### 2. Launch
With Docker running, start the services using Docker Compose:
```bash
docker-compose up --build
```
The application will be accessible at the following endpoints:
*   **Frontend UI**: `http://localhost:4200`
*   **Backend API Docs**: `http://localhost:8000/docs` (Swagger UI)

## Roadmap
The following roadmap outlines areas for future exploration, focusing on applying advanced architectural patterns and strengthening the system's robustness and scalability.

*   **Architecture & Refactoring:**
    *   **Evolve to Hexagonal Architecture:** Formally refactor the backend by defining clear "Ports" (the application's core use cases) and "Adapters" (for external technologies like Supabase or Mistral). This would further decouple the core domain logic from infrastructure concerns.
    *   **Introduce Domain-Driven Design (DDD) Concepts:** Clarify the "Bounded Contexts" within the application (e.g., `DocumentIngestion` vs. `AnalysisInterpretation`). Define Aggregates (like a `Document` with its `AnalysisResult`) and Value Objects to create a more expressive and resilient domain model.

*   **Frontend Modernization & DX:**
    *   **Full Signal Adoption:** Complete the migration from RxJS-based patterns to a fully signal-based architecture for state management and component communication, creating a more modern and unified codebase.
    *   **Evaluate Testing Frameworks:** Assess migrating the unit testing framework from Karma/Jasmine to **Jest**. This could offer performance improvements, an integrated "all-in-one" framework with superior mocking, and a better overall developer experience.

*   **Backend & Scalability:**
    *   **Integrate Local, Privacy-Focused Agents:** Implement alternative agents using on-device models like **`docTR`** for OCR and **`Ollama`** for LLM analysis, offering users a fully offline and private processing option.
    *   **Decouple with a Message Queue:** To improve fault tolerance, replace the direct call to the `DocumentProcessor` with a message queue (e.g., RabbitMQ, Redis Streams). This would allow the API to return immediately after upload, with background workers consuming jobs from the queue.
    *   **Introduce a Caching Layer:** Implement a caching strategy (e.g., using Redis) for external API calls to AI services to reduce latency and costs.

*   **Security & Observability:**
    *   **Implement Authentication:** Integrate a full authentication system (e.g., Supabase Auth) and apply Row-Level Security (RLS) to the database to ensure data privacy.
    *   **Enhance Monitoring:** Implement structured logging and integrate with an observability platform (e.g., Prometheus/Grafana) to track application performance, errors, and system health.

## License
This project is for personal, non-commercial use only. Please see the [LICENSE.md](LICENSE.md) file for more details.
