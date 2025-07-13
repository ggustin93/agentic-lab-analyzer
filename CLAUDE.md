w# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Health Document Analyzer - A full-stack application for analyzing medical lab documents using Angular 19 frontend, Python FastAPI backend, and agent-based AI processing. The system extracts text via OCR, structures data with AI agents, and provides real-time feedback through Server-Sent Events.

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
- **Modular agent system**: Swappable agents for OCR (`MistralOCRService`) and analysis (`ChutesAIAgent`)
- **Asynchronous processing**: FastAPI handles concurrent document processing
- **Database migrations**: Supabase PostgreSQL with version-controlled migrations in `supabase/migrations/`

### Key Data Flow
1. Document upload → `DocumentProcessor.process_document()` → Storage in Supabase
2. Async agent pipeline: OCR extraction → AI analysis → Structured data persistence  
3. SSE streaming of status updates via `/api/v1/documents/{id}/stream`
4. Frontend consumes SSE for real-time UI updates using `DocumentAnalysisService.trackDocumentAnalysis()`

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

- **Unit tests**: Angular services and components with Jasmine/Karma
- **Integration tests**: Document lifecycle testing with `HttpClientTestingModule`
- **E2E tests**: Full user flows with Cypress, using API mocking for consistent testing
- **CI/CD**: GitHub Actions runs linting, unit tests, and production builds on every push

## File Structure Notes

- `src/app/services/document.store.ts`: Central signal-based state management
- `backend/services/document_processor.py`: Core orchestration logic  
- `backend/agents/`: AI agent implementations
- `supabase/migrations/`: Database schema changes
- `memory-bank/`: Project context and architectural decisions
- `.cursor/rules/`: Cursor IDE configuration rules