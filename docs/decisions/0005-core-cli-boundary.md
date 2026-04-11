# ADR-0005: Architectural Import Boundary

## Status

Accepted

## Context

`td` is structured with `src/td/core/` for business logic and
`src/td/cli/` for the Click frontend. This split only pays off if
`core/` is importable without `cli/` being present. Otherwise the
"library" half of the split is fictional and the split is decorative.

Two failure modes would silently undo the separation:

1. `core/` imports a CLI-only concern (Click types, Rich output,
   `OutputFormatter`) for convenience. The next person sees the
   import and assumes it's fine.
2. `cli/` injects logic into `core/` via a plugin registry or
   runtime-resolved import that doesn't appear in the static import
   graph.

Either path makes `core/` depend on `cli/`, and the ability to embed
`td.core` in another Python project disappears without warning.

## Decision

**`core/` must not import from `cli/`, ever, in any form.**

- No `from td.cli import ...` statements in `core/`
- No `importlib.import_module("td.cli...")` indirection
- No runtime-dispatch mechanism that reaches into `cli/` from `core/`

`cli/` may import freely from `core/`. Cross-cutting concerns that
touch both layers (output formatting, error shaping, schema
generation) live in `cli/` and consume plain data from `core/`.

Enforced by a tier-3 architectural test that scans every module in
`src/td/core/` for imports matching `td.cli` and fails the test suite
if any are found. See `CONTRIBUTING.md` testing philosophy for the
tier definitions.

## Consequences

**Positive.** `core/` is genuinely standalone. A downstream project
could depend on `td.core` without pulling Click, Rich, or Textual.
The import graph tells you the full dependency shape at a glance.
Refactors that would accidentally couple the layers fail CI
immediately rather than at runtime or in review.

**Negative.** When a cross-cutting concern emerges, it must live in
`cli/` and accept plain data from `core/`. This sometimes feels
backwards. A recent example: error suggestions would be more
convenient if attached directly to exceptions raised in `core/`.
Mitigation: `core/` raises typed exceptions with structured data, and
`cli/errors.py` maps them through `map_api_exception()` to `TdError`
subclasses with human suggestions. The translation layer is small
and explicit.

**Non-obvious.** "Plain data from `core/`" means Python builtins,
dataclasses, or typed exception classes. It does *not* mean Click
objects, Rich renderables, or anything that imports from a UI
library. If you're reaching for such a type inside `core/`, stop.
