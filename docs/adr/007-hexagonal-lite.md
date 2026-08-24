# ADR-007: Hexagonal-lite: ports for volatile dependencies only

- Status: Accepted
- Date: 2026-08

## Context

The README roadmap lists "evolve to hexagonal architecture" and an internal
SOLID review found two concrete violations: presentation logic inside the
persistence layer (`DatabaseManager` formatted API responses and markdown),
and a `DocumentProcessor` singleton created at module import in `main.py`
with no composition root. The question is how far toward ports-and-adapters
a proof-of-concept should honestly go.

## Options considered

1. **Full hexagonal**: ports for every infrastructure dependency
   (persistence, storage, agents), a domain core with no framework imports.
   Correct in the large; at this scale it is ceremony without a measurable
   benefit, and it would double the file count of a ~15-module backend.
2. **Status quo**: leaves the two violations in place; the "swappable
   agents" claim was already made real (ADR-002 era work), but tests keep
   patching module globals.
3. **Hexagonal-lite**: draw ports only where dependencies are volatile or
   substitution is actually exercised (the AI agents, via the Protocols in
   `agents/base.py`); move presentation out of persistence into a pure
   module; make `main.py` a real composition root
   (`get_document_processor()` behind `Depends`, built lazily).

## Decision

Option 3. Concretely: `services/document_presenter.py` holds the pure
response-shaping functions; `DatabaseManager` is persistence only;
endpoints receive the processor through FastAPI dependency injection, and
tests substitute it with `app.dependency_overrides` instead of patching.

## Consequences

- The seams the project claims are the seams that exist, nothing more.
- API tests no longer patch import-time globals; the presenter is unit-
  tested as plain functions.
- Deliberately deferred, with explicit triggers: splitting `DatabaseManager`
  into per-aggregate repositories (trigger: a second consumer of a subset
  of its interface; see backlog 016), and full ports for persistence and
  storage (trigger: a concrete need to swap them, e.g. the local-first
  variant sketched in ADR-006). *Update 2026-08: the second trigger fired;
  persistence/storage ports were introduced in [ADR-008](008-local-first-persistence.md).*
