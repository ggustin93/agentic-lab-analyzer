# ADR-006 — Cloud OCR (Mistral) over local OCR

- Status: Accepted
- Date: 2025-07 (recorded retroactively)

## Context

Lab reports arrive as PDFs or photos with complex table layouts. The OCR
stage must preserve *table structure* (marker / value / unit / range
columns), not just extract text. This decision sends health data to a
third-party processor, so it is a privacy decision as much as a technical one.

## Options considered

1. **Tesseract (local)** — data never leaves the machine, but raw text output
   loses table structure; rebuilding columns from coordinates is a project in
   itself.
2. **Local vision model** — structure-aware and private, but GPU requirements
   are out of scope for a PoC.
3. **Mistral OCR API** — returns per-page *markdown with tables intact*,
   which is exactly what the downstream extraction prompt consumes; an
   EU-based provider (relevant for GDPR posture).

## Decision

Mistral OCR (`mistral-ocr-latest`), returning structured markdown per page.

## Consequences

- Document content transits to Mistral's API: users must be informed
  (intended-use statement in the README) and no real personal documents
  belong in demo environments — `scripts/purge_demo_data.py` exists for that.
- The provider is swappable behind the `OCRAgent` protocol
  (`agents/base.py`); a privacy-first local option is the natural evolution
  if the project ever exceeds PoC scope.
