# Tech Context: Lab Insight Engine

## 1. Frontend

- **Framework:** Angular (latest version)
- **State Management:** RxJS
- **Styling:** Tailwind CSS
- **Real-time Communication:** Server-Sent Events (SSE) via the native `EventSource` API.
- **Testing:** Jasmine and Karma for unit tests.

## 2. Backend

- **Framework:** FastAPI (Python)
- **Data Persistence:** Supabase (PostgreSQL)
- **AI/OCR Services:**
    - Mistral for OCR and data extraction.
    - Chute AI for generating insights (or another similar LLM).
- **Configuration:** Pydantic
- **Testing:** pytest

## 3. Development Environment

- **Containerization:** Docker & Docker Compose
- **Version Control:** Git & GitHub
- **CI/CD:** GitHub Actions

## 4. Technical Constraints

- **File Size Limit:** The system is designed to handle file uploads up to 10MB.
- **File Types:** The system accepts `.pdf`, `.png`, and `.jpg` files.
- **Single-Tenant:** The MVP is designed for a single user/tenant.
- **Security:** API keys and database connection strings MUST be managed via environment variables and not be committed to source control.

## 5. Tooling

- **Supabase MCP:** We have access to the Supabase MCP tools, allowing for direct programmatic interaction with Supabase services. 