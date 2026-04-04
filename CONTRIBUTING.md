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
