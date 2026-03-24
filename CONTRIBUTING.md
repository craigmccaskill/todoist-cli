# Contributing to td

Thanks for your interest in contributing! Here's how to get started.

## Development Setup

1. Clone the repo and install in editable mode with dev dependencies:

```bash
git clone https://github.com/craigmccaskill/todoist-cli.git
cd todoist-cli
python -m venv .venv
source .venv/bin/activate
pip install -e ".[dev]"
```

2. Install pre-commit hooks:

```bash
pre-commit install
```

## Running Checks

```bash
# Lint
ruff check .
ruff format --check .

# Type check
mypy td/

# Tests (CI enforces 85% minimum coverage)
pytest

# All at once
ruff check . && ruff format --check . && mypy td/ && pytest
```

## Making Changes

1. Create a branch from `main`
2. Make your changes
3. Ensure all checks pass (lint, types, tests)
4. Update `CHANGELOG.md` under `[Unreleased]` if the change is user-facing
5. Open a pull request

## Code Style

- **Framework**: Click (not Typer) — we own the output/schema/completions layer
- **Architecture**: `td/core/` is pure business logic with no CLI dependency. `td/cli/` is the thin Click frontend
- **Output**: All commands use `OutputFormatter` for Rich/JSON/Plain modes
- **Errors**: All errors use structured `TdError` subclasses with codes and suggestions
- **Types**: Full type annotations. `mypy --strict` must pass

## Adding a New Command

1. Add business logic in `td/core/<module>.py`
2. Add Click command in `td/cli/<module>.py`
3. Register the command in `td/cli/__init__.py`
4. Add output methods to `td/cli/output.py` if needed
5. Add tests in `tests/`
6. Run `td schema` to verify the command appears in the manifest

## Questions?

Open an issue — happy to help.
