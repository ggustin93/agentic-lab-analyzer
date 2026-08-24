# 015 — OCR quality gate with three-way routing

- Severity: Medium · Priority: Could · Labels: responsible-ai, data-quality,
  backend, frontend

## Context

The pipeline currently treats every OCR result as good enough to analyze:
a poorly scanned document produces a degraded analysis that looks exactly
like a trustworthy one. Before considering a "better" OCR model or any
per-laboratory tuning, the system needs to *know* when its input quality is
insufficient — and say so. This is risk-based triage applied to documents:
route by measured quality rather than trusting uniformly.

## Expected behavior

Each document receives a composite quality score after the OCR and
extraction stages, and is routed three ways: auto-accepted, flagged for
human review, or rejected with an explicit "document unreadable — please
re-scan" outcome. A degraded result is never presented silently as a normal
one.

## Business rules

- The score combines cheap, auditable signals (weights configurable, each
  signal logged individually): tabular structure detected in the OCR output
  (markdown tables vs. flat text); proportion of table cells successfully
  parsed; markers extracted vs. expected density; plausibility violations
  (per-marker bounds, e.g. a hemoglobin of 145 g/dL indicates a unit
  error); schema-validation retries consumed; test date resolved or null.
- Thresholds are **calibrated on the evaluation corpus** (issue 011) from a
  risk–coverage curve — the auto-accept rate vs. residual error trade-off
  is chosen explicitly and recorded, not asserted.
- Review routing surfaces the doubtful fields highlighted next to the
  source document (the existing PDF viewer provides most of this UI).
- The score and route are persisted with the analysis (extends provenance,
  issue 010).

## Edge cases

Handwritten annotations over printed values; multi-page documents where
only one page is degraded; documents that are readable but are not lab
reports at all (should reject with a distinct reason).

## Validation intent (acceptance criteria)

- Given a clean synthetic report, then it is auto-accepted and its stored
  record carries the score and route.
- Given the same report with injected OCR noise above the calibrated level,
  then it routes to review, and the UI shows which fields triggered it.
- Given a blank or non-lab document, then it is rejected with an explicit
  reason — no analysis record is presented as complete.
- Given the evaluation corpus, then the calibration report (risk–coverage
  curve and chosen thresholds) is committed alongside the thresholds.

## Out of scope (deliberate)

Switching OCR providers (only justified if the gate's error analysis shows
OCR — not extraction or parsing — is the measured bottleneck); per-lab
fine-tuned OCR models (see research notes §8 for why this is not pursued);
a full review/annotation workflow with audit trail.

## Assumptions / open questions

Depends on 011 (corpus) for calibration and pairs naturally with 010
(provenance). The expected-marker-density signal needs a modest prior per
document type; start with a global one and refine per lab profile if those
are introduced.
