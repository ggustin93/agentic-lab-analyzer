# ADR-001 — Angular signals over RxJS/NgRx for state management

- Status: Accepted
- Date: 2025-07 (recorded retroactively)

## Context

The frontend needs reactive state for a document list, per-document processing
progress, loading flags and errors, consumed by OnPush components. The
Angular ecosystem offers three mainstream options: NgRx (Redux-style store),
plain RxJS subjects in services, or the Angular 16+ signals API, which
Angular 19 makes the idiomatic default.

## Options considered

1. **NgRx** — battle-tested, devtools, but heavy ceremony (actions, reducers,
   effects, selectors) for an app with a single aggregate (documents).
2. **RxJS BehaviorSubjects** — familiar, but manual subscription management
   in every component and easy to leak.
3. **Signals** (`signal`/`computed`/`update`) — synchronous, glitch-free
   reads, automatic fine-grained change detection with OnPush, no
   subscriptions to manage in templates.

## Decision

Signals, held in a single `DocumentStore` (`src/app/services/document.store.ts`)
that exposes `computed()` selectors and immutable `update()` mutations. RxJS
remains at the edges where it is the right tool: HTTP calls and route params.

## Consequences

- Components read state directly in templates with no async pipe or
  subscription lifecycle.
- The store is trivially testable (pure signal reads after mutations).
- SSE events still arrive as callbacks and are bridged into the store by the
  orchestration service — that bridge is the one place where the two worlds
  meet, and it must stay the only one.
