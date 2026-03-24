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

## Branching

- Work on feature branches: `feat/description`, `fix/description`, `docs/description`
- PR into `main`
- CI must pass before merge
- Keep PRs focused — one issue per PR when possible

## Making Changes

1. Create a branch from `main`: `git checkout -b feat/my-feature`
2. Make your changes
3. Run `make check` (must pass)
4. Update `CHANGELOG.md` under `[Unreleased]` if the change is user-facing
5. Commit with conventional commit message
6. Push and open a pull request

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

Maintainers only:

```bash
make release VERSION=0.2.0
```

This bumps the version, updates CHANGELOG.md, commits, tags, and pushes. The CI release workflow handles PyPI publishing.

## Questions?

Open an issue — happy to help.
