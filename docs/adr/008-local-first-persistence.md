# ADR-008: Local-first persistence: SQLite + local files behind ports

- Status: Accepted
- Date: 2026-08

## Context

The original Supabase project was deleted, leaving the application unable to
run at all, which is precisely the trigger ADR-007 reserved for introducing
full persistence ports: *"a concrete need to swap them, e.g. the local-first
variant"*. Separately, a clone-and-run experience matters for a public
repository: requiring a cloud database account to try a PoC is friction with
no payoff.

## Decision

Introduce two `Protocol` ports (`services/ports.py`) mirroring the existing
manager surfaces (`DocumentRepository` and `FileStorage`) and select the
adapter pair in the composition root (`main.py`) from `STORAGE_MODE`:

- **`local` (default)**: `LocalDatabaseManager` (stdlib `sqlite3`, WAL, one
  shared connection behind a lock) and `LocalStorageManager` (files under
  `UPLOAD_DIR`, served back by a `StaticFiles` mount at `/api/v1/files/`).
- **`supabase`**: the original adapters, unchanged; their credentials are
  now validated only when this mode is selected.

Supporting choices:

- **Stdlib `sqlite3`, synchronous.** The Supabase adapter already ran
  synchronous calls inside async endpoints; a local read is microseconds
  where the old path was an HTTPS round-trip. `aiosqlite` would force
  `async` through eleven method signatures for no measurable gain.
- **Schema as one idempotent `schema.sql`** (SQLite dialect) executed at
  adapter init; no migration framework for a three-table schema.
  `supabase/migrations/` remains the source of truth for the Supabase mode.
- **`health_markers` kept** despite being write-only today, so both adapters
  stay behavior-identical.
- **Local URLs.** `public_url` becomes `{PUBLIC_BASE_URL}/api/v1/files/{path}`.
  This works for both consumers: the browser's PDF viewer (CORS already
  covers it) and the OCR client, which downloads the file itself and sends
  base64 to Mistral, so the URL never needs to be publicly reachable.

## Consequences

- The repository runs with only the two AI keys; tests and contract tests
  run with none.
- The local adapters are covered by contract tests against a real SQLite
  file and directory (`tests/test_local_persistence.py`); the Supabase
  adapters keep mock-based coverage, since contract-testing a mock proves
  nothing.
- `DocumentProcessor` no longer builds its own dependencies; adapters are
  injected, completing the composition-root pattern of ADR-007.

## Out of scope (deliberate)

- `aiosqlite` (trigger: measured event-loop stalls)
- SQLite migration tooling (trigger: a schema change while local data must survive)
- Per-aggregate repository split: backlog 016, trigger unchanged
- Local OCR/LLM: backlog 017; this ADR only removes the *database* cloud dependency
- Auth/signed URLs on `/api/v1/files/`: single-user local demo; auth is backlog 003
