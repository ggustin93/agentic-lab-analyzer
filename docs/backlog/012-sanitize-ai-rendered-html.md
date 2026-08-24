# 012: Sanitize AI-rendered HTML

- Severity: Medium · Priority: Should · Labels: security, frontend

## Context

AI-generated markdown is rendered via `marked.parse()` into `[innerHTML]`
(`ai-insights.component`). Angular's sanitizer blocks script execution, but
content/markup injection passes, the hand-rolled markdown fallback escapes
nothing, and the tooltip directive defaults to `allowHTML = true` (which
bypasses Angular's sanitizer entirely via tippy.js).

## Expected behavior

Model output is treated as untrusted at the rendering boundary: sanitized
explicitly before insertion, independent of framework defaults.

## Business rules

- DOMPurify (allow-list of formatting tags) over `marked` output before
  binding.
- The markdown fallback escapes HTML entities before its transformations.
- `allowHTML` defaults to `false` on the tooltip directive; the one static
  usage that needs HTML opts in explicitly.

## Validation intent (acceptance criteria)

- Given insight text containing `<img onerror=...>` and a phishing anchor,
  then the rendered DOM contains neither an event handler nor the anchor's
  href (links restricted or stripped).
- Given a tooltip bound to arbitrary text, then it renders as text by
  default.

## Out of scope (deliberate)

CSP headers (belongs to deployment configuration).

## Assumptions / open questions

Whether KaTeX output requires an extended allow-list: to verify against
DOMPurify defaults.
