# ADR-0011: Dependency tracking between issues

## Status

Accepted

## Context

Issues in the `td` project frequently depend on each other. Two
shapes of dependency matter:

1. **Hierarchical.** One issue is a parent of several children.
   Example: an epic issue that breaks down into sub-issues, a
   milestone tracker that references each item in the milestone,
   or a single coordinating issue that spawns a set of related
   small tasks.
2. **Cross-cutting.** One issue blocks another without being its
   parent. Example: #15 (Natural language actions) is blocked by
   foundation work that hasn't happened yet. Or #27 (MCP server
   mode) depends on the JSON output envelope being stable (ADR-0002)
   before MCP can expose it as a contract.

Milestone planning needs to see both shapes at once. Without
explicit tracking, it's easy to schedule a blocked item into a
milestone that can't actually ship it, or to miss that an "epic"
item is actually five sub-issues that should each have their own
classification, priority, and pre-work.

GitHub Projects v2 does not have a first-class *"blocks / blocked
by"* field type. The realistic options for capturing dependencies
are:

1. **Informal keywords in issue body or comments.** Write `"Depends
   on #N"` or `"Blocks #N"` in plain prose. Zero tooling overhead.
   Not queryable without grep, easy to miss during review.
2. **GitHub task lists** in parent issues referencing children.
   Native UI support. GitHub automatically surfaces the relationship
   on each child as a "tracked by" link. Hierarchical only.
3. **A project field** called `Blocked by` (text or single-select).
   Visible in project views. Manual maintenance, no semantic link,
   drifts from reality fast.
4. **A dedicated dependency map doc** at `docs/dependency-map.md`
   with a Mermaid graph or markdown list. Version-controlled and
   reviewable, but drifts fast because nothing forces it to match
   current issue state.
5. **A GitHub Action parser** that reads keyword dependencies from
   issue bodies and maintains a bot comment with the current state.
   Self-maintaining once built. Requires building and maintaining
   the Action.

## Decision

Use a **hybrid of (2) and (1):**

- **Hierarchical dependencies** use GitHub task lists in the parent
  issue. GitHub automatically surfaces the relationship on each
  child as a "tracked by" link. No convention needed, native
  behavior.
- **Cross-cutting dependencies** use formal keywords in the issue
  body (*not* comments, so they stay visible above the fold and are
  grep-able across the repo):

  ```
  Blocks: #N
  Blocked by: #N
  ```

Both are checked during milestone planning to avoid scheduling work
that can't actually start yet.

## Consequences

**Positive.**

- Native GitHub features cover hierarchical tracking with zero
  maintenance overhead. No tooling to build or keep running.
- Keyword convention is simple, grep-able across the repo, and
  doesn't require automation.
- Both mechanisms are visible where the work is: task lists on the
  parent issue, keywords on the blocked issue itself.
- Migration path stays open. If the manual convention breaks down
  later, the GitHub Action parser (option 5) reads the same
  keywords without requiring changes to existing issues.

**Negative.**

- Cross-cutting dependencies are only as reliable as the discipline
  to add the keywords. Forgetting to add them has no mechanical
  safety net.
- Hierarchical task lists do not capture semantic intent (*"blocks"*
  vs *"tracks"* vs *"child of"*). GitHub shows a single
  relationship type.
- The `Blocks` and `Blocked by` keywords need to stay in sync across
  both issues. Removing a dependency means editing both.
- Keyword parsing is purely by convention today. No validation, no
  enforcement, no errors if you typo the keyword.

**Discipline.** During triage (see the decision framework ADR), scan
the issue body for `Blocks:` and `Blocked by:` lines and act on
them. During milestone planning, walk the task list of any tracker
issue before assigning its children into the milestone. Revisit
option 5 (GitHub Action parser) if manual tracking proves
insufficient after one or two milestone cycles.
