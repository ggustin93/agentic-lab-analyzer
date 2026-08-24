# 017 — Local OCR adapter: Docling vs. PaddleOCR bake-off

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

**PaddleOCR/PaddleX** offers a second credible candidate family:
`PP-StructureV3-lightweight` for full-page layout analysis (text, tables,
formulas → markdown; ~3.7 s/page CPU in the vendor's own benchmark), and
the `table_recognition` pipeline with `SLANet_plus` (6.9 MB, ~42 ms CPU per
table crop) as a table-structure specialist. Vendor figures, to be
re-measured on our corpus. Note the input-shape distinction: this pipeline
receives *full report pages*, so the realistic full-page duel is Docling
vs. PP-StructureV3; SLANet_plus becomes relevant as a second stage behind a
table-detection step. Plain-text engines (Tesseract, RapidOCR) are not
candidates here — they do not reconstruct table structure, which is this
project's actual bottleneck.

Either way this is an **additional adapter behind the existing `OCRAgent`
protocol** (`agents/base.py`), not a replacement: the point is a measured
comparison, and incidentally the concrete proof that the pipeline's agents
are swappable.

## Expected behavior

A local adapter implementing `extract_structured_data(file_url)` with the
same output contract ({pages: [{index, markdown}]}), selectable through
configuration (`OCR_PROVIDER=mistral|docling|paddle`); the evaluation
harness (011) runs the same corpus through every adapter and reports the
quality/latency/privacy trade-off.

## Business rules

- Same output schema as the Mistral adapter — downstream stages unchanged.
- Selection via a settings flag (`OCR_PROVIDER`), wired in the composition
  root.
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
  per-field extraction quality and per-document latency for Mistral vs.
  Docling vs. PP-StructureV3-lightweight — the quality/privacy frontier of
  research notes §5, made concrete with measured (not vendor) numbers.
- Given the existing test suite, then a fake conforming to `OCRAgent`
  still satisfies both wirings (protocol unchanged).

## Out of scope (deliberate)

Local LLM extraction (Ollama) — same logic, separate item if the OCR
comparison proves worthwhile; GPU deployment; replacing Mistral by default
(only a measured result would justify it, per backlog 015's gate logic).

## Assumptions / open questions

Docling's OCR-engine choice for scans needs its own small bake-off, and
SLANet_plus is only worth wiring if table *detection* on full pages proves
reliable; whether
document *download* stays (URL-based contract) or the adapter reads bytes
directly is decided when 004 (signed URLs) lands.
