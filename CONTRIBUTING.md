# Contributing to td

Thanks for your interest in contributing! Here's how to get started.

## Development Setup

1. Clone the repo and install in editable mode with dev dependencies:

```bash
git clone https://github.com/craigmccaskill/todoist-cli.git
cd todoist-cli
python -m venv .venv
source .venv/bin/activate
make install
```

2. Verify everything works:

```bash
make check
```

## Common Commands

```bash
make help       # Show all available targets
make check      # Run lint + tests (the one command you need)
make fmt        # Auto-format code
make test       # Run tests only
make lint       # Run linter + type checker only
make examples   # Regenerate docs/examples.md
make clean      # Remove build artifacts
```

## Commit Messages

We use [Conventional Commits](https://www.conventionalcommits.org/) for clear history and automated changelogs.

**Format:** `<type>(<scope>): <description>`

**Types:**

| Type | When to use |
|------|-------------|
| `feat` | New feature or command |
| `fix` | Bug fix |
| `docs` | Documentation only |
| `refactor` | Code change that neither fixes a bug nor adds a feature |
| `test` | Adding or updating tests |
| `ci` | CI/CD workflow changes |
| `chore` | Maintenance (deps, config, tooling) |

**Examples:**
```
feat(tasks): add td undo command
fix(output): handle empty task list in plain mode
docs: update README with MCP section
refactor(core): simplify project name resolution
test(errors): add coverage for rate limit mapping
ci: add coverage threshold to CI
chore(deps): bump rich to v14
```

**Scope** is optional but encouraged — use the module name (`tasks`, `output`, `errors`, `config`, `core`, `ci`, `deps`).

## Workflow

### Issue-first

All work is tracked in GitHub Issues. Issues are for planning and backlog — creating an issue
does not immediately trigger work. When it's time to code, pick from existing issues, either
individually or grouped by theme.

### Milestones

Before starting a batch of work, create a GitHub milestone (e.g. "v0.8.0") and assign the
target issues. The milestone defines what ships in that release:

- **Scope is defined upfront** — we know what's in a release before we start
- **Progress is visible** — milestone shows X/Y issues closed
- **Release trigger is mechanical** — milestone 100% complete → cut the release
- **Hotfixes bypass this** — critical bugs get a PATCH release immediately

#### Planning a milestone

After assigning issues, prepare each one before coding starts:

1. **Identify dependencies** — which issues must land before others? Document the
   suggested ordering so work flows without blocking.
2. **Define "done"** — each issue should have explicit acceptance criteria beyond
   "code merged." How do we verify the fix works? Manual test? New automated test?
   Integration check?
3. **Specify testing expectations** — what new tests does each issue need? Not every
   fix needs a test (e.g., a 2-line config change), but the decision should be explicit.
4. **Group into PRs** — related issues can share a PR (e.g., two aspects of the same
   bug). Document which issues will be combined to avoid duplicate work.
5. **Handle housekeeping first** — merge pending dependency updates, clean up stale
   branches, and resolve any blocking infrastructure issues before starting feature work.

Document all of this in issue comments so the plan is visible to anyone picking up the work.

#### Batch anti-patterns

The milestone process above works for batches of similar small work
(fixes, refactors, additive options). It breaks down when it starts
producing the following patterns:

- **Rolling multiple design decisions into one batch issue.**
  *"Complete CRUD for X"* is a category, not an issue. Each command
  with design variance gets its own issue. Batch-scoped issues hide
  per-command decisions under a single checkbox, and the *"Before
  starting work"* comment applies once to the category when it should
  apply to every design decision inside it. This is the pattern that
  produced issue #250.
- **Dumping 20 issues into a milestone in 20 minutes.** That's a
  backlog dump, not a plan. Plan issues are individually decomposed
  and prioritized before execution starts. If the milestone-planning
  session felt like a brainstorm, the plan is not ready.
- **Treating dashboard progress as a forcing function.** An 18-of-20
  milestone is not a reason to skip reconsidering the 19th issue. The
  release can wait. If the *"X of Y closed"* count is the thing
  pressuring you to push through a design call you're uncertain
  about, stop and re-examine.
- **Heterogeneous issues in a single milestone.** A mix of small-bug
  work and design-heavy work in one batch means the pre-work rigor
  gets applied unevenly. Consider splitting into two milestones when
  the work types diverge.

### Project board conventions

The GitHub Project classifies every issue across five single-select
fields. These conventions are enforced during triage so the
classification stays current.

**`Status`** — where the work is in its lifecycle:

| Value | Meaning |
|---|---|
| `Backlog` | Filed, not yet scheduled. Default for new issues. |
| `Ready` | Triage complete. Prepared to be picked up. |
| `In flight` | PR is open for this work. Set automatically when the PR opens. |
| `Blocked` | Waiting on something external (e.g. PEP resolution, upstream fix). Manual. |
| `Done` | PR merged or issue closed. Set automatically. |

**`Tier`** — what kind of work is this, and how much pre-work it requires:

| Value | Meaning |
|---|---|
| `Needs triage` | Default for new issues until classified. |
| `Trivial` | Typo, one-liner, dependency bump. No pre-work required. |
| `Standard` | Single command, single bug, single refactor. 5-item pre-work comment required. |
| `Needs ADR` | New command grammar, output shape change, new architectural invariant. Standard comment plus a proposed ADR linked before the PR opens. |
| `Exploratory` | Spike or research. Scope the investigation, then decide whether to proceed. |

**`Priority`** — how urgent it is:

| Value | Meaning |
|---|---|
| `P0` | Literal emergency. Production broken or security issue live. Drop everything. |
| `P1` | Important. Pick up soon, before normal rotation. |
| `P2` | Normal. Default for new work. |
| `P3` | Someday. Backlog of ideas without deadlines. |

**`Size`** — rough effort estimate, orthogonal to `Tier`:

| Value | Meaning |
|---|---|
| `S` | Small, a few hours at most. |
| `M` | Medium, most of a day. |
| `L` | Large, multiple days. Consider splitting if possible. |

**`Theme`** — category of work, for cross-cutting views:

| Value | Meaning |
|---|---|
| `Infrastructure` | CI, build, packaging, deps, tooling, cross-cutting machinery. |
| `DX` | Contributor experience (working on the codebase). |
| `UX` | End-user experience (using the CLI). |
| `Polish` | Cosmetic refinement, copy, small behavioral cleanup. |

**Mandatory at triage:** `Tier`, `Size`, and `Priority` must all be
set before an issue leaves the triage queue. `Theme` and labels are
strongly encouraged but not blocking.

### Dependency tracking

Dependencies between issues come in two shapes. Track them in two
different places:

**Hierarchical** (parent with children). Use a GitHub task list in
the parent issue referencing the children. GitHub automatically
surfaces the "tracked by" relationship on each child. Good for epic
and sub-issue relationships.

**Cross-cutting** (A blocks B, but they aren't parent/child). Add
formal keywords to the issue body (*not* comments, so they stay
visible above the fold and are grep-able across the repo):

```
Blocks: #N
Blocked by: #N
```

Check both during milestone planning to avoid scheduling work that
can't start yet.

### Before starting work

Different kinds of change need different amounts of pre-work. Classify
the issue first, then apply the matching ritual.

| Tier | Examples | Pre-work required |
|---|---|---|
| **Trivial** | typo, one-line fix, dependency bump, CI tweak | Optional: commit message is enough |
| **Standard** | single command, single bug fix, single refactor | A comment on the issue with the five items below, before a branch exists |
| **Design-affecting** | new command grammar, output shape change, new architectural invariant | Standard comment **plus** a proposed ADR linked in the issue before the PR opens (see *Architecture Decision Records* below) |

**Standard pre-work comment (five items):**

1. **Root cause** — what you found during investigation
2. **Approach** — what you'll do and why
3. **Risks / open questions** — anything that could go wrong or needs clarification
4. **Definition of done** — how do we verify this is actually fixed?
5. **Testing** — what new tests are needed, if any?

**Size triggers.** Any change over 200 lines or touching more than
three modules cannot be classified as *Trivial*. It must be at least
*Standard*, and the author must explicitly consider whether it
crosses into *Design-affecting*. Size alone does not force the
Design-affecting tier, but it forces the question.

This creates a paper trail for decisions, catches bad assumptions
early, and helps future contributors understand context without
re-investigating.

### Bug fixes require regression tests

Every bug fix PR must include a test that would have caught the bug. The test should target
the **root cause**, not just verify the fix works. Examples:

- Architecture violation → test that scans imports to enforce the boundary
- File permissions bug → test that checks `stat().st_mode` after write
- Silent failure → test that an unexpected exception type propagates

This prevents the same class of bug from recurring and builds up the test suite in the areas
that matter most. If a fix genuinely doesn't need a test (e.g., a typo in a comment), document
why in the PR.

### Branch → PR → Merge

1. Create a branch from `main`: `feat/description`, `fix/description`, `docs/description`
2. Implement the change, updating `CHANGELOG.md` (see below)
3. Run `make check` before pushing
4. Open a PR with `Closes #X` in the body (or multiple `Closes #X` for themed work)
5. CI must pass
6. Squash merge to main

Merging a PR automatically moves the linked issue's `Status` to
`Done`, and opening a PR that references an issue (via `Closes #N`
or a similar keyword) moves the linked issue to `In flight`. Both
transitions run on GitHub Projects v2 built-in workflows (the
*Pull request merged* and *Pull request linked to issue* rules).
No manual board updates required, no PAT or GitHub App needed.

Feature branches merge directly to main. No long-lived release branches.
Keep PRs focused — one issue per PR when possible.

### CHANGELOG

Update `CHANGELOG.md` under `[Unreleased]` in every PR — all changes, not just user-facing.
CLI users are developers who appreciate transparency. Organize entries under:

- **Added** — new commands, features, options
- **Changed** — modifications to existing behavior, refactors, performance
- **Fixed** — bug fixes
- **Internal** — tests, CI, dependency bumps, architecture changes

**Style:** Write entries for humans, not commit logs. Each entry should explain what changed,
why it matters, and show usage when applicable. Use code blocks for commands and config
examples. The changelog is the first place users look when upgrading — make it useful.

```markdown
- **Batch task completion** — knock out multiple tasks in one command (#194)
  \`\`\`
  td done 2 4        # complete rows 2 and 4 from your last td ls
  \`\`\`
  Each task is completed independently. If one fails, the rest still go through.

- **Error messages are human-readable** — no more raw `400 Bad Request` (#195)
  \`\`\`
  Before:  Error: API error: 400 Bad Request
  After:   Error: Bad request: Invalid due date
           Suggestion: Check command arguments. Use --help for usage details.
  \`\`\`
```

## Testing Philosophy

Tests should cover three tiers:

### Tier 1: Unit tests

Mock external dependencies, test business logic in isolation. This is the majority of the
test suite — pure functions, data transformations, CLI output formatting.

### Tier 2: Boundary tests

Test that integration points actually work. **Don't mock the thing you're testing against.**

- **SDK**: verify parameter names and types match the real API (inspect signatures, don't
  call the live API)
- **TUI**: Textual pilot tests that simulate keypresses headless
- **Filesystem**: verify permissions, atomic writes, corrupt file handling
- **Config**: round-trip through TOML parse/write

### Tier 3: Architectural tests

Assert structural invariants that should never be violated:

- `core/` never imports from `cli/` (scan imports)
- No bare `except Exception` outside documented exceptions
- All commands registered in schema
- All CLI commands use `OutputFormatter`

These tests are cheap to write, rarely change, and catch entire categories of bugs at once.

## Design Principle

> **Canonical version:** [ADR-0001: Design Principle](docs/decisions/0001-design-principle.md).
> The content below is a human-readable mirror. Updates to the principle
> are made via a superseding ADR, then mirrored back to this section.

**Surface the context users need to be successful, nothing more.**

Every command, error message, and output should be measured against this. The CLI should feel
like a tool built for the person using it, not a wrapper around an API.

### Accept what the user means, not what the system needs

The common case should be flag-free. If a command has one obvious argument, accept it
positionally. Flags exist for disambiguation and advanced use, not basic operations.

```bash
td sections Blog          # obvious intent — scope to project
td completed Work         # same pattern
td ls -p Work --sort due  # flags for the less common case
```

### Show what's useful, not what the API returns

Rich and Plain modes are for humans. IDs belong in JSON output for scripting.

- Tables show row numbers, names, dates — not opaque IDs
- Empty states explain what to do next, not just "no results"
- Success messages confirm what happened in human terms

### Help the user recover when things go wrong

Every error should answer three questions: what happened, why, and what to do next.

- Ambiguous input triggers a picker instead of an error
- Missing arguments launch interactive mode instead of printing usage
- Suggestions are specific: "Run `td projects` to see available names"

### Progressive disclosure

The simple case is simple. Power features are available but not in the way.

```bash
td add call dentist                              # day one
td add "call dentist" -p Health --due tomorrow   # week two
```

## Architecture Decision Records

Design decisions that matter live in
[`docs/decisions/`](docs/decisions/README.md) as Architecture Decision
Records (ADRs). Each ADR is a one-page Nygard-format document capturing
a single decision: context, decision, consequences. See the
[decisions README](docs/decisions/README.md) for the full format,
immutability rules, scope heuristic, and writing process.

**When an ADR is required.** A proposed ADR must be linked in the
issue *before* the PR opens if the change:

- Introduces a new command grammar or renames an existing one
- Changes the JSON output envelope (see ADR-0002) or adds a new
  `type` value
- Changes the interpretation of the design principle in ADR-0001
- Adds or changes an architectural invariant (example: the `core/` to
  `cli/` import boundary from ADR-0005)
- Supersedes or deprecates an existing accepted ADR

Everything else does not need an ADR. Code comments, commit messages,
and CHANGELOG entries are the right tools for tactical changes.

## Code Style

- **Framework**: Click (not Typer) — we own the output/schema/completions layer
- **Architecture**: `td/core/` is pure business logic with no CLI dependency. `td/cli/` is the thin Click frontend
- **Output**: All commands use `OutputFormatter` for Rich/JSON/Plain modes
- **Errors**: All errors use structured `TdError` subclasses with codes and suggestions
- **Types**: Full type annotations. `mypy --strict` must pass
- **Coverage**: CI enforces 85% minimum

## Adding a New Command

1. Add business logic in `td/core/<module>.py`
2. Add Click command in `td/cli/<module>.py`
3. Register the command in `td/cli/__init__.py`
4. Add output methods to `td/cli/output.py` if needed
5. Add tests in `tests/`
6. Update the schema test expected commands set
7. Run `td schema` to verify the command appears in the manifest

**Design checklist** (measure every new command against the design principle):

- [ ] Common case is flag-free — obvious positional args accepted
- [ ] Tables show useful context, not raw IDs
- [ ] Errors include a message, reason, and suggestion
- [ ] Empty states guide the user on what to do
- [ ] Rich/JSON/Plain modes all work and are consistent
- [ ] If this command introduces or changes a design decision (command grammar, output shape, invariant), a proposed ADR is linked before the PR opens
- [ ] This command serves end users of Todoist, not project maintainers.
      Maintainer tooling (triage, release, audits) belongs in Claude
      skills, GitHub Actions, or scripts under `.github/` or `scripts/`,
      not the public CLI. See ADR-0001 "CLI surface boundary".

## Releasing

PRs squash merge to main continuously. The CHANGELOG accumulates under `[Unreleased]`.

A release is cut when a milestone reaches 100% completion:

1. Review `[Unreleased]` in CHANGELOG to confirm the version bump
2. Run `make release VERSION=x.y.z`
3. After CI passes and PR merges, tag and push

Critical bug fixes get a PATCH release immediately without waiting for a milestone.

## Versioning

Follows semver: `0.MINOR.PATCH[-prerelease]`

### Pre-1.0 (current)

- **MINOR** (0.X.0) — themed batch of work. New commands, significant features, architectural
  changes. Bump this for each milestone release.
- **PATCH** (0.X.Y) — bug fixes, dependency bumps, small corrections that don't warrant waiting
  for the next milestone. Pressure valve for regressions.
- **Pre-release tag** — `-alpha` while the command set and output formats are still shifting.
  Move to `-beta` when the CLI surface and JSON envelope stabilize. Drop the tag for 1.0.

### 1.0 criteria

- Command set is stable (no more renames or removals)
- JSON output envelope is a contract, not best-effort
- Published to PyPI/Homebrew (users can't easily pin to a commit)
- Breaking changes warrant a major bump going forward

### Post-1.0

- **MAJOR** — breaking changes to CLI flags, JSON output format, config file format
- **MINOR** — new commands, options, output fields
- **PATCH** — bug fixes, performance, internal changes

## Questions?

Open an issue — happy to help.
