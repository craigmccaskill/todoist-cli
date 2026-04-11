# ADR-0003: Priority Number Mapping

## Status

Accepted

## Context

The Todoist API represents priority with inverted numbers compared to
user expectations:

- API: `4` = urgent, `3` = high, `2` = normal, `1` = low
- User mental model (from Todoist's own UI labels): `p1` = urgent,
  `p2` = high, `p3` = normal, `p4` = low

Mixing these two number spaces causes silent bugs. An agent or user
who assumes `p1` means API value 1 creates a low-priority task when
they meant urgent. The bug does not fail any test: the task saves
successfully with the wrong priority, and the user only notices when
the task doesn't appear at the top of their list.

Two options:

1. **Match the API.** Accept API numbers everywhere, rely on
   documentation and memory. Rejected because *"my p1 task is showing
   as low priority"* is the predictable failure mode, and it happens
   silently.
2. **Match the user.** Convert at every boundary between display and
   API, so the rest of the codebase speaks one language.

## Decision

Use the formula `display = 5 - api_priority` (equivalently,
`api = 5 - display`) at every boundary between the display layer and
the API layer. The formula is symmetric: applying it twice returns
the original value.

- **User input.** Always parses `p1` through `p4` as display numbers
  and converts to API numbers before the HTTP call.
- **User output.** Always converts API numbers back to display
  numbers before rendering in any mode (Rich, Plain, or JSON).
- **Internal storage.** Logs, caches, and schema all standardize on
  display numbers. The API number exists only in the HTTP
  request/response body.

## Consequences

**Positive.** Users and agents never see API numbers. The whole
codebase speaks one priority language. Every translation point is
localized to the API boundary (`todoist-api-python` call sites).

**Negative.** Every priority reference must go through the formula.
Missing a conversion is a latent bug that passes silently. Mitigation:
tests assert both directions at API boundary points, and the formula
is called out in `CLAUDE.md` as a known gotcha so anyone touching
priority code sees the rule.

**Non-obvious.** When writing a new command that handles priority,
the rule is *never* accept, display, or store raw API priority
numbers outside the translation layer. If you find yourself typing
`priority=4` anywhere in `core/` or `cli/`, that's almost certainly
a bug.
