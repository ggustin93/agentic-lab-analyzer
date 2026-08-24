# Remediation backlog

This backlog documents the findings of a structured audit of this
proof-of-concept (security, responsible-AI, architecture, and testing),
triaged and prioritized deliberately. Each item follows the same
specification template — expected behavior, business rules, edge cases,
constraints, validation intent (acceptance criteria), what is intentionally
out of scope, and open questions — so that it can be converted into a GitHub
issue as-is.

Two prioritization lenses are used and they intentionally disagree:
**severity** reflects technical risk; **priority** reflects value ÷ effort
for the project's current goal (a credible, honest PoC). An item can be
severity-critical yet scheduled late when a documented mitigation captures
most of its value (see `001`–`004`).

| # | Title | Severity | Priority | Status |
|---|-------|----------|----------|--------|
| [001](001-server-side-upload-validation.md) | Server-side upload validation | High | Should | Done |
| [002](002-bounded-sse-streams.md) | Bounded SSE streams | High | Should | Done |
| [003](003-authentication-and-user-scoping.md) | Authentication & per-user scoping | Critical | Could* | Open |
| [004](004-rls-and-private-storage.md) | Row Level Security & private storage | Critical | Could* | Open |
| [005](005-rate-limiting.md) | Rate limiting & processing locks | High | Should | Open |
| [006](006-generic-error-messages.md) | Generic client-facing error messages | Medium | Should | Done |
| [007](007-deterministic-out-of-range.md) | Deterministic out-of-range flag | High | Should | Open |
| [008](008-native-structured-outputs.md) | Native structured outputs | Medium | Should | Open |
| [009](009-async-ocr-client.md) | Non-blocking OCR HTTP client | High | Should | Done |
| [010](010-analysis-provenance.md) | Analysis provenance metadata | Medium | Should | Open |
| [011](011-prompt-evaluation-harness.md) | Prompt evaluation harness | Medium | Could | Open |
| [012](012-sanitize-ai-rendered-html.md) | Sanitize AI-rendered HTML | Medium | Should | Open |
| [013](013-test-coverage-gaps.md) | Close targeted test coverage gaps | Medium | Should | Open |
| [014](014-processing-task-lifecycle.md) | Processing task lifecycle | Medium | Could | Open |
| [015](015-ocr-quality-gate.md) | OCR quality gate with three-way routing | Medium | Could | Open |
| [016](016-repository-split.md) | Split DatabaseManager into repositories | Low | Could† | Open |

† Deferred with an explicit trigger (see the issue) — recorded so the deferral is a decision, not an omission.

\* Deliberately scheduled behind a documented mitigation: the project runs
locally with synthetic data, and README section 8 states these limitations
openly. They become non-negotiable before any deployment.

Already addressed during the initial hardening pass (kept for the record):
repository hygiene (committed bytecode, duplicate files), documentation
aligned with the actual code, ISO 8601 date validation with rejection of
ambiguous formats, server-enforced medical disclaimer, JSON "cleaning" that
could corrupt valid output, dependency updates for known CVEs, agent
contracts (`agents/base.py`) aligned and injected, backend CI re-enabled.
