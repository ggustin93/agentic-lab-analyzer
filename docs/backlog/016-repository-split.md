# 016 — Split DatabaseManager into per-aggregate repositories

- Severity: Low · Priority: Could (deferred with an explicit trigger) ·
  Labels: architecture, backend

## Context

`DatabaseManager` exposes ~12 public methods spanning three aggregates
(documents, analysis results, health markers). Presentation has already been
extracted (`document_presenter.py`, ADR-007); what remains is a wide
persistence interface whose consumers each use only a subset — an interface-
segregation smell that is tolerable while there is exactly one consumer per
subset.

## Expected behavior

When triggered, three narrow repositories (`DocumentRepository`,
`AnalysisRepository`, `MarkerRepository`) with Protocol contracts, each
owning one aggregate; `DocumentProcessor` and `ProcessingPipeline` receive
only the repositories they use.

## Trigger (deliberately not "now")

Implement when a second consumer of a subset of the persistence interface
appears (a CLI, a scheduled job, the startup recovery pass of backlog 014),
or when auth scoping (003) forces per-aggregate query changes anyway.
Until then the split would be movement without benefit — recorded here so
the deferral is a decision, not an omission.

## Validation intent (acceptance criteria)

- Given the split, then no consumer imports a repository it does not call.
- Given the existing test suite, then it passes unchanged apart from
  constructor wiring — behavior is identical.

## Out of scope (deliberate)

Full hexagonal ports for storage and persistence (see ADR-007's triggers);
any ORM introduction.
