# Changelog

Notable changes, grouped by phase. Dates reflect the actual commit history.

## 2026-08 — Local-first persistence (ADR-008)

- `STORAGE_MODE=local` (new default): SQLite + local uploads folder behind new `DocumentRepository` / `FileStorage` ports — the repo now runs with only two AI keys, no cloud database account.
- Supabase kept as the optional second adapter; its credentials are validated only when selected.
- Contract tests for the local adapters against a real SQLite file and directory; `DocumentProcessor` now takes its adapters by constructor injection.
- Backend Docker image fixed for current Debian slim (`libgl1`, `libxrender1`).
- Insight model switched to `Qwen/Qwen3.8-27B-TEE` — the previously pinned Chutes model was retired from the catalog.

## 2026-08 — Hardening pass

- Security: server-side upload validation (size bound, magic-bytes content type), bounded SSE streams, generic client-facing error messages, async OCR client.
- Architecture: hexagonal-lite refactor — `Protocol` agent contracts, composition root with FastAPI `Depends`, presenter extraction (ADR-007).
- Product artifacts: 7 ADRs, specified backlog (18 items, mirrored as GitHub issues), lab-marker extraction spec, AI-workflow guardrails doc, research notes.
- Housekeeping: MIT license, stack-specific `.gitignore`, Docker guides consolidated into `docs/docker.md`, backend README rewritten for the actual stack, synthetic demo data in screenshots, backend tests enabled in CI, Dependabot grouped updates merged.
- Backend test suite grown from 22 to 36 tests (API validation, presenter, conftest for secret-free runs).
- History rewrite: development scratch files removed from the repository and its history.

## 2025-07 — v1.1 (proof-of-concept refinements)

- Structured OCR data handling through the pipeline; `HealthMarker` model with flexible value types; refined extraction rules (trend arrows, historical columns, malformed reference ranges).
- ISO 8601 date validation — ambiguous dates rejected, never guessed.
- Frontend: 4-stage real-time progress (SSE), retry flows, toast notifications.

## 2025-07 — v1.0 (initial MVP, 12-day build)

- Angular 19 frontend (signals, standalone components, OnPush), FastAPI backend, agent pipeline (Mistral OCR → Mistral Large extraction → Chutes.AI insights), Supabase persistence, Docker Compose environment, CI for the frontend, Cypress happy-path E2E.
