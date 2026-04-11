# ADR-0004: Task Reference Resolution Order

## Status

Accepted

## Context

Users reference tasks in commands like `td done`, `td edit`, `td show`,
and `td delete` using several styles:

- Row number from a recent `td ls` output: `td done 3`
- Content substring: `td done "call dentist"` or `td done dentist`
- Raw Todoist task ID: `td done 6C7Q8pJQvVr2fR4h`

All three need to work without the user having to declare which kind
of reference they're using. The resolver needs a deterministic order
that produces the right answer for the common case while degrading
gracefully when the reference is ambiguous or uses a less-common form.

## Decision

Resolution order, first match wins:

1. **Row number.** If the reference is all digits and matches a row
   from the cached last-list result (see ADR-0007 for the 10-minute
   TTL), treat as a row number and resolve to the cached task ID.
2. **Content match.** If the reference is a string with length > 2
   that did not match a row, fuzzy-match against task content.
   Multiple matches trigger an interactive picker in a TTY, or an
   `ambiguous_match` error when piped.
3. **Raw task ID.** If nothing above matches, pass the reference
   through to the API as a task ID. Let the API reject it if invalid.

Implementation lives in `cli/tasks.py:_resolve_task()` and calls into
`core/cache.py:resolve_task_ref()` for the row-number lookup.

## Consequences

**Positive.** The common case (*"complete row 3"*) is one keystroke.
The power case (*"complete this specific ID"*) still works. Ambiguity
surfaces as a picker, not a silent wrong-task.

**Negative.** Row numbers depend on cache freshness. A user who runs
`td ls`, walks away for 11 minutes, and returns to `td done 3` hits a
stale cache. The 10-minute TTL is a heuristic (see ADR-0007), tunable
via `cache_ttl_results` in `config.toml`. Fuzzy content match can
also select the wrong task if the match is too loose; the `len > 2`
guard and the picker-on-ambiguity rule prevent the silent wrong case.

**Non-obvious ordering rationale.** Row numbers must win over task
IDs because Todoist task IDs can start with digits, and a bare `3` is
far more likely to be row 3 than task ID `3`. Content matches must
come after row numbers because `td done 3` almost always means row 3,
not a task literally titled `3`.
