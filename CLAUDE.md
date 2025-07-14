# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Table of Contents

1. [Project Overview](#project-overview)
2. [Commands](#commands)
3. [Architecture](#architecture)
4. [Backend File Structure](#backend-file-structure)
5. [Frontend Advanced Features](#frontend-advanced-features)
6. [Signal-Based State Management](#signal-based-state-management)
7. [Environment Configuration](#environment-configuration)
8. [Testing Strategy](#testing-strategy)
9. [File Structure Notes](#file-structure-notes)

## Project Overview

**Lab Insight Engine v1.1** - A professional-grade medical document analysis platform showcasing enterprise Angular 19 patterns, agent-based AI architecture, and production-ready testing infrastructure. Built as a portfolio piece demonstrating senior frontend engineering expertise with real-time processing, comprehensive testing, and modern TypeScript patterns.

## Commands

### Frontend (Angular 19)
```bash
# Development server
npm start                    # Serves on localhost:4200

# Build and test
npm run build               # Production build
npm run lint                # ESLint linting
npm test                    # Unit tests with Karma/Jasmine
npm run test:docker         # Headless tests in Docker
npm run test:coverage       # Tests with coverage report

# End-to-end testing
npm run e2e                 # Run Cypress tests
npm run e2e:open            # Open Cypress UI
npm run e2e:docker          # E2E tests in Docker

# Combined testing
npm run test:all:docker     # Run all tests in Docker
```

### Backend (Python/FastAPI)
```bash
# Development (from backend/ directory)
python main.py              # Run FastAPI server on localhost:8000
python -m pytest           # Run backend tests
python -m pytest tests/test_document_processor.py  # Run specific test

# Environment setup
pip install -r requirements.txt
cp .env.example .env        # Configure environment variables
```

### Docker Environment
```bash
docker-compose up --build   # Full stack development
docker-compose run --rm cypress  # Run E2E tests in container
```

## Architecture

### Frontend Architecture
- **Angular 19 with Signals**: Modern reactive state management using Angular signals instead of traditional RxJS patterns
- **Three-tier service architecture**:
  - `DocumentApiService` (`src/app/services/document-api.service.ts`): HTTP client communication
  - `DocumentStore` (`src/app/services/document.store.ts`): Signal-based state management
  - `DocumentAnalysisService` (`src/app/services/document-analysis.service.ts`): Business logic orchestration
- **OnPush change detection**: Performance-optimized components
- **Real-time updates**: Server-Sent Events (SSE) for live document processing status

### Backend Architecture
- **Agent-based orchestration**: `DocumentProcessor` (`backend/services/document_processor.py`) coordinates workflow between AI agents
- **Modular agent system**: Swappable agents for OCR (`MistralOCRService`) and analysis (`InsightAgent`)
- **Chain of Responsibility Pattern**: Specialized agents with clean separation of concerns
- **Asynchronous processing**: FastAPI handles concurrent document processing
- **Database migrations**: Supabase PostgreSQL with version-controlled migrations in `supabase/migrations/`
- **Robust error handling**: JSON parsing, retry mechanisms, and comprehensive logging

### Key Data Flow
1. Document upload → `DocumentProcessor.process_document()` → Storage in Supabase
2. Async agent pipeline: OCR extraction → AI analysis → Structured data persistence  
3. SSE streaming of status updates via `/api/v1/documents/{id}/stream`
4. Frontend consumes SSE for real-time UI updates using `DocumentAnalysisService.trackDocumentAnalysis()`

## Backend File Structure

```
backend/
├── agents/
│   └── base.py                     # Abstract base class for AI agents with common interface
├── config/
│   └── settings.py                 # Centralized configuration management with Pydantic
├── data/                           # Static data and reference files
├── models/
│   ├── document_models.py          # Pydantic models for document-related data structures
│   └── health_models.py            # Medical domain models (HealthMarker, reference ranges)
├── services/
│   ├── database_manager.py         # Supabase database operations and connection management
│   ├── document_processor.py       # Core orchestration logic for document processing pipeline
│   ├── extraction_agent.py         # OCR text extraction using Mistral AI vision models
│   ├── insight_agent.py            # Clinical analysis and insights generation with AI
│   ├── json_utils.py               # Robust JSON parsing with error handling and cleanup
│   ├── mistral_ocr_service.py      # Mistral AI integration for optical character recognition
│   ├── processing_pipeline.py      # Multi-stage document processing workflow management
│   └── storage_manager.py          # File storage operations and cloud storage integration
├── tests/
│   ├── test_document_processor_refactored.py  # Comprehensive pipeline testing with mocks
│   ├── test_json_utils.py          # JSON parsing and data validation test suite
│   └── test_mistral_ocr.py         # OCR service integration and error handling tests
├── Dockerfile.backend              # Production-ready containerization configuration
├── main.py                         # FastAPI application entry point and API route definitions
├── README.md                       # Backend-specific documentation and setup instructions
└── requirements.txt                # Python dependencies with version pinning
```

### Key Backend Patterns

- **Agent Pattern**: Each AI service implements `BaseAgent` with consistent `process()` interface
- **Service Layer**: Clear separation between API routes, business logic, and data access
- **Error Resilience**: Comprehensive exception handling with user-friendly error messages
- **Type Safety**: Full Pydantic model validation throughout the processing pipeline
- **Testing Strategy**: Unit tests with 100% coverage of critical paths and error scenarios

## Frontend Advanced Features

### Modern Angular 19 Patterns Applied
- **Standalone Components**: No NgModules, improved tree-shaking and performance
- **Control Flow Syntax**: `@if/@else/@for` replacing `*ngIf/*ngFor` for better type safety
- **inject() Function**: Dependency injection without constructor pollution
- **OnPush Strategy**: Optimized change detection for all components
- **Signal-based Architecture**: Reactive state management replacing RxJS where appropriate

### Portfolio-Worthy Features
- **Real-time Progress Tracking**: 4-stage visual pipeline (OCR → AI Analysis → Saving → Complete)
- **Color-coded Status System**: Yellow/Blue/Purple/Green progression with animated indicators
- **Professional Error Handling**: Comprehensive retry mechanisms with user feedback
- **TypeScript Excellence**: Strict mode enabled with advanced type safety patterns
- **Component Composition**: Reusable, testable components following SOLID principles
- **Performance Monitoring**: Lazy loading, OnPush optimization, and bundle analysis

### Advanced UI/UX Patterns
- **Responsive Design**: Mobile-first approach with Tailwind CSS utility classes
- **Accessibility (a11y)**: ARIA labels, keyboard navigation, and screen reader support
- **Loading States**: Skeleton screens, progress indicators, and optimistic updates
- **Error Boundaries**: Graceful error handling with recovery options
- **Toast Notifications**: Non-intrusive user feedback with auto-dismiss
- **Data Visualization**: Interactive tables with filtering, sorting, and highlighting

## Signal-Based State Management

The frontend uses Angular 19 signals extensively. Key patterns:

```typescript
// State access (reactive)
readonly documents = computed(() => this.documentStore.documents());
readonly isLoading = computed(() => this.documentStore.isUploading());

// State mutations
this.documentStore.addDocument(document);
this.documentStore.setUploadLoading(true);
```

## Environment Configuration

- Frontend: Environment-specific configs in `src/environments/`
- Backend: `.env` file in `backend/` directory with API keys for Mistral AI, Chutes.AI, and Supabase credentials

## Testing Strategy

### Test Coverage Summary (Current Status)
- ✅ **Frontend**: 22/22 unit tests passing (100% success rate)
- ✅ **Backend**: 22/22 tests passing (100% success rate)  
- ✅ **Linting**: All files pass ESLint validation
- ✅ **Build**: Production build successful (1.32 MB bundle)

### Testing Architecture
- **Unit Tests**: Angular services and components with Jasmine/Karma
  - Document lifecycle testing with `HttpClientTestingModule`
  - Signal-based state management validation
  - Error handling and edge case coverage
- **Backend Tests**: pytest with comprehensive mocking
  - Document processor pipeline testing
  - JSON parsing and error resilience
  - OCR service integration validation
- **E2E Tests**: Cypress with Docker containerization
  - Full user journey simulation
  - API mocking for consistent testing
  - Cross-browser compatibility validation
- **Performance Testing**: Bundle analysis and load testing
- **CI/CD Pipeline**: GitHub Actions with automated testing on every commit

### Quality Assurance
- **TypeScript Strict Mode**: Full type safety with no `any` types
- **ESLint Configuration**: Enforced code quality and consistency
- **Test-Driven Development**: Critical paths covered before implementation
- **Docker Testing Environment**: Consistent testing across all environments

## File Structure Notes

- `src/app/services/document.store.ts`: Central signal-based state management
- `backend/services/document_processor.py`: Core orchestration logic  
- `backend/agents/`: AI agent implementations
- `supabase/migrations/`: Database schema changes
- `memory-bank/`: Project context and architectural decisions
- `.cursor/rules/`: Cursor IDE configuration rules