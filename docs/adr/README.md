# Architecture Decision Records

Every structural decision in this project is recorded here in a lightweight
[MADR](https://adr.github.io/madr/) format: context, options considered,
decision, and consequences (including the ones we accept knowingly).

ADRs are immutable once accepted; a change of direction gets a new ADR that
supersedes the old one, so the reasoning trail stays auditable.

| # | Decision | Status |
|---|----------|--------|
| [001](001-angular-signals-over-rxjs-state.md) | Angular signals over RxJS/NgRx for state | Accepted |
| [002](002-hand-rolled-pipeline-over-langgraph.md) | Hand-rolled agent pipeline over LangGraph/PydanticAI | Accepted |
| [003](003-two-stage-llm-pipeline.md) | Extraction and insights as two separate LLM calls | Accepted |
| [004](004-sse-over-websockets.md) | SSE polling over WebSockets or Supabase Realtime | Accepted |
| [005](005-supabase-as-backend-platform.md) | Supabase (BaaS) over self-managed Postgres | Accepted |
| [006](006-cloud-ocr-over-local.md) | Cloud OCR (Mistral) over local OCR | Accepted |
| [007](007-hexagonal-lite.md) | Hexagonal-lite: ports for volatile dependencies only | Accepted |
| [008](008-local-first-persistence.md) | Local-first persistence: SQLite + local files behind ports | Accepted |
