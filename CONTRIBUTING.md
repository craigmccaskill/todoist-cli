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

### Before starting work

Before coding on an issue, add a comment to the issue with:

1. **Root cause** — what you found during investigation
2. **Approach** — what you'll do and why
3. **Risks / open questions** — anything that could go wrong or needs clarification
4. **Definition of done** — how do we verify this is actually fixed?
5. **Testing** — what new tests are needed, if any?

This creates a paper trail for decisions, catches bad assumptions early, and helps future
contributors understand context without re-investigating.

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

Feature branches merge directly to main. No long-lived release branches.
Keep PRs focused — one issue per PR when possible.

### CHANGELOG

Update `CHANGELOG.md` under `[Unreleased]` in every PR — all changes, not just user-facing.
CLI users are developers who appreciate transparency. Organize entries under:

- **Added** — new commands, features, options
- **Changed** — modifications to existing behavior, refactors, performance
- **Fixed** — bug fixes
- **Internal** — tests, CI, dependency bumps, architecture changes

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
