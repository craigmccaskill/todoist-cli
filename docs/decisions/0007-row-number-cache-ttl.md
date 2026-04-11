# ADR-0007: Row-Number Cache TTLs

## Status

Accepted

## Context

`td` maintains two caches to make subsequent commands fast and
ergonomic:

1. **Result cache** (`last_results.json`). Maps row numbers from the
   most recent list command (`td ls`, `td today`, `td inbox`, etc.)
   to task IDs. Enables `td done 3` to resolve row 3 back to the
   right task via ADR-0004.
2. **Names cache** (`names.json`). Project, label, and section name
   to ID mappings. Enables `td add "fix bug" -p Work` to avoid an
   API lookup for "Work" every time.

Both caches must expire, because:

- The result cache becomes wrong when tasks are added, completed, or
  reordered elsewhere (web UI, mobile, another session).
- The names cache becomes wrong when projects or labels are renamed
  or deleted.

Too-short TTLs undermine the ergonomic benefit: the user lists tasks,
answers an email, comes back, runs `td done 3`, and row 3 is no
longer valid. Too-long TTLs produce stale results that silently
resolve to wrong tasks or invalid project IDs.

## Decision

- **Result cache: 10 minute TTL** by default. Covers the common
  "list then act within a few minutes" pattern.
- **Names cache: 5 minute TTL** by default. Shorter because name
  changes (renames) need to propagate faster, and because the cost
  of a names-cache miss is cheap (one API call that refreshes the
  whole mapping).

Both TTLs are configurable via `config.toml`:

```toml
cache_ttl_results = 600  # seconds, default 10 minutes
cache_ttl_names = 300    # seconds, default 5 minutes
```

Storage location follows XDG: `$XDG_CACHE_HOME/td/` (default
`~/.cache/td/`).

## Consequences

**Positive.** The common "list, then act" workflow works without
surprising the user. Power users with long-running terminals or
unusual latency requirements can tune both TTLs in config without
a code change.

**Negative.** The defaults are a compromise: too short for some
users, too long for others. The config escape hatch is the answer,
but discoverability is limited. Mitigation: cache-miss failure modes
are non-silent (row-number lookup falls through to content match,
then to API task-ID passthrough, per ADR-0004).

**Non-obvious.** The 10-minute result TTL is intentionally longer
than the 5-minute names TTL, not the other way around. Task-list
staleness is usually tolerable for minutes (you just relist if
needed), but a renamed project should take effect quickly so the
user doesn't see the old name the next time they type an ambiguous
project reference. Reversing these defaults would make the
rename-then-add failure more common.
