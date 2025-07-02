# System Patterns: Lab Insight Engine

## 1. Backend Architecture

- **Agent-Based Design:** The backend uses a protocol-based (interface) design for its AI agents (`chutes_ai_agent.py`, `mistral_ocr_service.py`). This is a key pattern for maintainability, allowing different agent implementations to be swapped without changing the core business logic in the `DocumentProcessor`.
- **Decoupled Orchestration:** The `DocumentProcessor` service acts as an orchestrator, coordinating the workflow (OCR, analysis, data persistence) but remaining decoupled from the specific AI services that perform the work.
- **Secure Configuration:** Pydantic's `Settings` model is used to manage all secrets and configuration from environment variables, ensuring no sensitive data is exposed in the codebase.
- **Layered API:** The FastAPI application exposes a versioned RESTful API (`/api/v1/...`) for clear separation and future scalability.

## 2. Frontend Architecture

- **Smart Service/Presentational Component:** The frontend follows a pattern where "smart" services (`DocumentAnalysisService`) contain the business logic, state management, and API interactions. "Presentational" components (`data-table`, `document-list`) are responsible only for displaying data and emitting user events, making them highly reusable and testable.
- **RxJS for State Management:** A centralized, RxJS-based service (`DocumentAnalysisService`) manages the application's state. This provides a reactive data flow that is efficient and scales well for this project's scope without requiring a larger state management library like NgRx or Redux.
- **OnPush Change Detection:** Components are configured with `OnPush` change detection strategy to optimize performance by reducing Angular's rendering cycles. **Enhanced with OnChanges lifecycle hooks for precise progress tracking and debugging.**
- **Lazy Loading:** Feature modules, particularly the `analysis` page, are lazy-loaded to minimize the initial bundle size and improve the First Contentful Paint (FCP) time.

## 3. Progress Tracking System

**NEW: Stage-Based Visual Feedback Pattern**
- **4-Stage Pipeline:** Consistent progress stages across the entire application (OCR Extraction → AI Analysis → Saving Results → Complete)
- **Color-Coded Theming:** Each stage has a distinct color theme (yellow → blue → purple → green) applied consistently across all UI components
- **Reactive Progress Updates:** Uses Angular's OnChanges and ChangeDetectorRef for precise progress tracking without unnecessary re-renders
- **SSE Progress Enhancement:** Backend `document_processor.py` includes progress percentage and stage information in Server-Sent Events for real-time updates
- **Visual State Synchronization:** Progress bars, spinners, icons, and stage indicators all update synchronously based on the same data source
- **Comprehensive Logging:** Detailed console logging at each progress update for debugging and monitoring

## 4. DevOps

- **Containerization:** The entire application stack (frontend, backend) is containerized using Docker and managed with Docker Compose. This ensures a consistent, reproducible development and deployment environment for any developer.
- **CI/CD Pipeline:** A GitHub Actions workflow automates linting and testing for both frontend and backend on every push, enforcing code quality and preventing regressions.

## 5. Database Schema Management

### **Migration System Architecture**
- **Version-controlled migrations** stored in `supabase/migrations/` with semantic naming
- **Naming convention**: `YYYYMMDD_NNN_description.sql` for chronological ordering
- **Rollback scripts** (`_rollback.sql` suffix) for safe schema reversions
- **Baseline documentation** capturing original schema state

### **Migration Structure**
```
supabase/
├── migrations/           # Schema changes with rollbacks
│   ├── README.md        # Migration guidelines
│   ├── 20250101_000_baseline_schema.sql
│   └── 20250102_001_add_progress_tracking_columns.sql
├── seeds/               # Initial/test data
└── types/               # TypeScript definitions
```

### **Current Schema Evolution**
1. **Baseline Schema** (20250101_000) - Core tables: documents, analysis_results, health_markers
2. **Progress Tracking** (20250102_001) - Added `progress` and `processing_stage` columns

### **Application Methods**
- **Supabase MCP** for automated, safe application via agent
- **Manual SQL Editor** for direct database access
- **Supabase CLI** for local development workflows
- **Safety features**: IF EXISTS/NOT EXISTS, proper indexes, documentation 