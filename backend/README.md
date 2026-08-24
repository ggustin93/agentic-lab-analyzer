# Backend: FastAPI document analysis API

Python 3.11 / FastAPI service that turns uploaded lab documents into
structured health markers and AI-generated insights. Architecture, security
posture, and trade-offs are documented in the [project README](../README.md)
and [`docs/adr/`](../docs/adr/).

## Pipeline

1. `MistralOCRService`: PDF/image → per-page markdown (Mistral OCR API)
2. `ExtractionAgent`: markdown → typed `HealthMarker`s (Mistral Large, Pydantic-validated)
3. `InsightAgent`: validated markers → summary and recommendations (Chutes.AI)
4. Persistence behind the ports in `services/ports.py` (ADR-008), selected by `STORAGE_MODE`: local SQLite + folder (default) or Supabase
5. SSE: processing stages streamed to the frontend

Agents are injected against the `Protocol` contracts in `agents/base.py`,
persistence adapters against `services/ports.py`; `main.py` is the
composition root (ADR-007/008). Response shaping lives in
`services/document_presenter.py`.

## API (prefix `/api/v1`)

| Method | Path | Purpose |
|---|---|---|
| POST | `/documents/upload` | Upload a document (202, async processing) |
| GET | `/documents/{id}/stream` | SSE processing status |
| GET | `/documents` | List documents |
| GET | `/documents/{id}` | Document with analysis |
| DELETE | `/documents/{id}` | Delete document + stored file |
| POST | `/documents/{id}/retry` | Re-run a failed analysis |

Interactive docs: `http://localhost:8000/docs`.

## Run

```bash
cd backend
pip install -r requirements.txt
cp .env.example .env        # fill in the Mistral and Chutes.AI keys; that's all
python main.py              # serves on localhost:8000
```

Local mode (default) stores data in `data/app.db` and files in `uploads/`.
Set `STORAGE_MODE=supabase` plus the Supabase variables for cloud persistence.

Or with Docker from the repo root: `docker compose up --build`
(see [`docs/docker.md`](../docs/docker.md)).

## Tests

```bash
python -m pytest            # fully mocked; no API keys needed (tests/conftest.py)
```

Covers the processor lifecycle and retries, upload validation and bounded SSE
(via `TestClient`), the async OCR client, ISO 8601 date validation, and the
presenter functions.
