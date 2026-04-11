# ADR-0001: Design Principle

## Status

Accepted

## Context

`td` has two audiences: humans at terminals and AI agents delegating
through the command tree. Without a shared principle, individual
commands drift toward whichever audience the author has in mind that
day. We saw this in PR #241, where CRUD commands followed the API's
shape (`project-edit`, `section-delete`) instead of user intent, and
produced the redesign called for in issue #250. The decision: establish
a single principle every command is measured against, so drift is
visible and correctable before it ships.

## Decision

**Surface the context users need to be successful, nothing more.**

Every command, error message, and output is measured against this.
The CLI should feel like a tool built for the person using it, not a
wrapper around an API.

Four sub-principles apply this rule:

### 1. Accept what the user means, not what the system needs

The common case should be flag-free. If a command has one obvious
argument, accept it positionally. Flags exist for disambiguation and
advanced use.

```bash
td sections Blog          # obvious intent: scope to project
td completed Work         # same pattern
td ls -p Work --sort due  # flags only for the less common case
```

### 2. Show what's useful, not what the API returns

Rich and Plain output modes are for humans. Raw IDs belong in JSON
output for scripting, not in tables.

- Tables show row numbers, names, and dates, not opaque IDs
- Empty states explain what to do next, not just "no results"
- Success messages confirm what happened in human terms

### 3. Help the user recover when things go wrong

Every error answers three questions: what happened, why, what to do
next.

- Ambiguous input triggers a picker instead of an error
- Missing arguments launch interactive mode instead of printing usage
- Suggestions are specific: *"Run `td projects` to see available names"*

### 4. Progressive disclosure

The simple case is simple. Power features exist but are not in the
way.

```bash
td add call dentist                              # day one
td add "call dentist" -p Health --due tomorrow   # week two
```

## Consequences

**Positive.** New commands have a concrete measuring stick: *"does
this conform to ADR-0001?"* is a review question, not a taste
judgment. The principle is citeable in PRs and makes divergences
visible. It covers both audiences (human and agent) without forcing
the author to pick sides.

**Negative.** Every new command requires explicit consideration, a
small tax on velocity for work that feels obvious. Some designs are
harder under the principle than under the API shape (see ADR-0009
for the CRUD verb grammar consequence). The principle is prescriptive
but not mechanically enforceable. Defense in depth: this ADR,
`CLAUDE.md`'s scoped "Adding a New Command or Changing Output Shape"
subsection, and `CONTRIBUTING.md`'s three-tier pre-work ritual.
