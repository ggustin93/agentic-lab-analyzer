# 001 — Server-side upload validation

- Severity: High · Priority: Should · Labels: security, backend

## Context

Upload validation currently exists only in the browser
(`upload-zone.component.ts`); `POST /api/v1/documents/upload` accepts any
payload and reads it fully into memory before any check. Client-side checks
are a UX convenience, not a control.

## Expected behavior

Every upload is validated server-side — size and content type — before any
byte reaches storage or the database.

## Business rules

- Maximum size: 10 MB (single source of truth in `config/settings.py`,
  read from the `MAX_FILE_SIZE` environment variable already present in
  `.env.example`).
- Accepted types: PDF, PNG, JPEG — determined from magic bytes
  (`python-magic` is already a dependency), never from the filename.
- Rejections are typed: `413` for size, `415` for type.

## Edge cases

Empty file; extension/content mismatch (`.pdf` containing an executable);
encrypted PDF; interrupted upload; content-type header absent or misleading.

## Constraints

Health-data context: a rejected file must leave no trace — no storage
object, no database row, no content in logs.

## Validation intent (acceptance criteria)

- Given an 11 MB file sent via `curl`, when POSTed, then `413` and no
  object exists in storage nor row in the database.
- Given an executable renamed `.pdf`, then `415` based on magic bytes.
- Given a valid 2 MB PDF, then the upload proceeds as today.

## Out of scope (deliberate)

Antivirus scanning; per-user quotas (depends on 003); streaming multipart
parsing (worth considering if the size limit ever grows).

## Assumptions / open questions

Is 10 MB sufficient for multi-page scanned reports? To verify against a
realistic corpus before hardening the limit.
