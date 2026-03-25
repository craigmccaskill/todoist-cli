# Contributing

## Development Setup

```bash
git clone https://github.com/craigmccaskill/todoist-cli.git
cd todoist-cli
pip install -e ".[dev]"
pre-commit install
```

## Commands

```bash
make check      # lint + test (the one command you need)
make fmt        # auto-format
make test       # tests only
make lint       # lint only
make examples   # regenerate docs/examples.md
make docs       # local docs preview
```

## Architecture

```
src/td/
  core/       # Pure business logic — no CLI dependency
  cli/        # Click commands and output formatting
  tui/        # Textual-based interactive components
  schema.py   # Click command tree → JSON capability manifest
```

The core is a library. The CLI is one frontend. The TUI is another. Both share the same business logic.

## Adding a Command

1. Add business logic to `src/td/core/` (if needed)
2. Add the Click command to `src/td/cli/`
3. Register in `src/td/cli/__init__.py`
4. Add tests
5. Update the schema test expected command set
6. Run `make check`

## Conventions

- **Conventional commits**: `feat(scope):`, `fix:`, `docs:`, `chore:`
- **mypy strict**: no `Any` without good reason
- **85% coverage minimum**: enforced in CI
- **ruff**: linting and formatting
