# Spec: Lab marker extraction

**Status:** implemented (v1) · maintained as the reference for extraction behavior
**Owner:** product/engineering (solo project)
**Implementation:** `backend/services/extraction_agent.py`, `backend/models/health_models.py`, `backend/services/json_utils.py`
**Related:** [ADR-003](../adr/003-two-stage-llm-pipeline.md) (two-stage pipeline) · backlog [007](../backlog/007-deterministic-out-of-range.md), [008](../backlog/008-native-structured-outputs.md), [011](../backlog/011-prompt-evaluation-harness.md)

This document specifies what the extraction stage must do, the business rules
it enforces, its known edge cases, and how each requirement is (or is not yet)
validated. It exists because "the LLM extracts the markers" is not a
specification: the value of this stage is exactly in the cases where a naive
reading of the document would produce a wrong number in a health context.

## 1. Problem

A lab report arrives as OCR output: per-page markdown preserving table
structure, in French, Dutch or English, from heterogeneous laboratory formats.
The system must produce a list of typed health markers (name, value, unit,
reference range, out-of-range flag) plus a document type and test date,
reliable enough to be displayed next to the original document.

## 2. Expected behavior

Input: the Mistral OCR JSON (`pages[].markdown`).
Output: a `HealthDataExtraction` object, shape-validated by Pydantic before
anything is persisted:

| Field | Type | Contract |
|---|---|---|
| `markers[].marker` | str | Marker name as printed on the report |
| `markers[].value` | str \| int \| float | Most recent result, arrows/whitespace stripped |
| `markers[].unit` | str \| null | Plain text (`mg/dL`), Unicode for Greek (`/μL`), `^` for powers, never LaTeX |
| `markers[].reference_range` | str \| null | Preserved verbatim (`3.5 - 5.0`, `< 2.0`); empty if absent |
| `markers[].is_out_of_range` | bool | See rule B3 |
| `document_type` | str | e.g. "Blood Test Report" |
| `test_date` | date \| null | ISO 8601 or null; never guessed (rule B1) |

## 3. Business rules

- **B1. Dates are rejected, not guessed.** Belgian/European reports are
  day-first (`DD/MM/YYYY`). The date order must be resolved from document
  language and context; if it cannot be determined unambiguously, `test_date`
  is `null`. A silently swapped day/month is a data-integrity error, not a
  formatting detail. Enforced twice: in the prompt, and deterministically in
  `json_utils.parse_date` (ISO 8601 or null).
- **B2. Most recent result only.** Columns labeled as historical
  ("Résultats Antérieurs", "Previous Results", or dated in the past) are
  ignored. With multiple unlabeled result columns, the leftmost is taken as
  most recent, the rest ignored: a stated assumption, not silent behavior.
- **B3. Out-of-range flag.** A trend arrow (`↗`/`↘`) printed next to a value
  is authoritative: the flag is `true`. Without an arrow, the value is
  compared to the reference range; when the status cannot be determined
  confidently, the flag defaults to `false` (under-flagging is preferred to
  false alarms in a document viewer where the original stays visible).
  *Known weakness:* the numeric comparison is currently performed by the LLM;
  making it deterministic post-processing is specified in backlog 007.
- **B4. Reference ranges verbatim.** Ranges keep the lab's own notation.
  Two known OCR corruption patterns are normalized (`<6 - 6.0` → `<6.0`,
  `>40 - 40` → `>40`); well-formed ranges are never altered.
- **B5. Output is untrusted until validated.** The model's JSON passes
  through `safe_json_parse` (markdown fences, trailing commas) and then
  Pydantic. A response that does not validate fails the stage; it is never
  partially persisted.

## 4. Edge cases

| Case | Expected handling |
|---|---|
| Trend arrows in value cell (`↗ 205`) | Strip to `205`; set `is_out_of_range = true` (B3) |
| Ambiguous date (`03/04/2025`, language unclear) | `test_date = null` (B1) |
| Historical result columns | Ignored (B2) |
| Marker table spanning pages | Pages correlated; one marker list for the document |
| Missing reference range | Empty string; flag follows B3's confidence rule |
| Non-numeric values (`positive`, `traces`) | Kept as strings; `value` is deliberately `str | int | float` |
| Malformed range from OCR (`<6 - 6.0`) | Normalized per B4 |
| LLM returns fenced/dirty JSON | Cleaned by `safe_json_parse`, else stage fails (B5) |

## 5. Out of scope (v1)

- Marker name normalization to a clinical ontology (LOINC); display uses the
  lab's own naming.
- Unit conversion (mg/dL ↔ mmol/L); values shown as printed.
- Deterministic range comparison: specified in backlog 007, not yet built.
- Multi-document trend analysis across reports.

## 6. Validation

| Requirement | How it is validated today |
|---|---|
| B1 date rejection | `backend/tests/test_json_utils.py` (ISO accepted, ambiguous → null) |
| B5 parse resilience | `backend/tests/test_json_utils.py` (fences, trailing commas, garbage) |
| Pipeline failure handling | `backend/tests/test_document_processor.py` (stage errors, retry) |
| Output shape | Pydantic models; invalid extractions raise, covered by processor tests |
| B2/B3/B4 prompt-level rules | **Not yet regression-tested**: they live in the prompt and are exercised manually against synthetic reports. A prompt evaluation harness with a graded synthetic corpus is specified in backlog [011](../backlog/011-prompt-evaluation-harness.md) + [018](../backlog/018-synthetic-corpus-generator.md); until it exists, prompt changes carry regression risk. |

Acceptance for any future change to this stage: the rules above hold on the
synthetic corpus, and no real patient document is ever used as a test fixture.
