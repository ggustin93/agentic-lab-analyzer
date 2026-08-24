# 017 — Docling-based local OCR adapter

- Severity: Low · Priority: Could · Labels: responsible-ai, privacy, backend

## Context

ADR-006 chose cloud OCR (Mistral) and recorded its consequence: document
content — health data — transits to a third party. The deliberate evolution
path is a local, privacy-first alternative. Docling (IBM, open source) is
the strongest current candidate for this project's specific need: it is
built around *layout and table-structure* extraction (TableFormer), exports
markdown per page — the exact shape our extraction stage already consumes —
and runs fully locally, with pluggable OCR engines (EasyOCR/Tesseract/
RapidOCR) for scanned inputs.

This is an **additional adapter behind the existing `OCRAgent` protocol**
(`agents/base.py`), not a replacement: the point is a measured comparison,
and incidentally the concrete proof that the pipeline's agents are
swappable.

## Expected behavior

A `DoclingOCRService` implementing `extract_structured_data(file_url)` with
the same output contract ({pages: [{index, markdown}]}), selectable through
configuration; the evaluation harness (011) can run the same corpus through
both adapters and report the quality/privacy trade-off.

## Business rules

- Same output schema as the Mistral adapter — downstream stages unchanged.
- Selection via a settings flag (e.g. `OCR_PROVIDER=mistral|docling`),
  wired in the composition root.
- Heavy model downloads happen at build/startup, never per request; CPU
  inference time is measured and reported, not assumed.

## Edge cases

Scanned (image-only) PDFs — requires the OCR-engine path, where local
quality is most likely to trail the cloud model; photos of documents;
multi-column layouts.

## Validation intent (acceptance criteria)

- Given `OCR_PROVIDER=docling`, then a document flows through the full
  pipeline with no change to extraction or insight stages.
- Given the evaluation corpus (011), then a side-by-side report exists:
  per-field extraction quality and per-document latency, Mistral vs.
  Docling — the quality/privacy frontier of research notes §5, made
  concrete.
- Given the existing test suite, then a fake conforming to `OCRAgent`
  still satisfies both wirings (protocol unchanged).

## Out of scope (deliberate)

Local LLM extraction (Ollama) — same logic, separate item if the OCR
comparison proves worthwhile; GPU deployment; replacing Mistral by default
(only a measured result would justify it, per backlog 015's gate logic).

## Assumptions / open questions

Docling's own OCR-engine choice for scans needs a small bake-off; whether
document *download* stays (URL-based contract) or the adapter reads bytes
directly is decided when 004 (signed URLs) lands.
