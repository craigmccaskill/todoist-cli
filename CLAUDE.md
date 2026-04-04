# CLAUDE.md — Project context for AI assistants

## What is this?

`td` — an AI-native Todoist CLI built for humans and AI agents. Python 3.10+, alpha (v0.7.0-alpha).

## Quick Reference

```bash
make check      # Run lint + tests (the one command before committing)
make fmt        # Auto-format code
make test       # Tests only (pytest, 85% coverage minimum)
make lint       # ruff check + ruff format --check + mypy strict
make install    # pip install -e ".[dev]" + pre-commit hooks
make examples   # Regenerate docs/examples.md
make docs       # Serve mkdocs locally
```

## Architecture

```
src/td/
├── core/          # Pure business logic — NO CLI dependency
│   ├── client.py      # TodoistAPI client construction + monitored session
│   ├── config.py      # TOML config loading/saving (XDG paths)
│   ├── tasks.py       # Task CRUD, filtering, sorting, fuzzy matching
│   ├── projects.py    # Project lookup, name mapping, inbox resolution
│   ├── labels.py      # Label operations
│   ├── sections.py    # Section operations
│   ├── cache.py       # Row-number result caching
│   └── rate_limit.py  # API rate limit monitoring via response headers
├── cli/           # Thin Click frontend
│   ├── __init__.py    # Main CLI group + command registration
│   ├── tasks.py       # Task commands (add, ls, done, edit, etc.)
│   ├── projects.py    # Project commands
│   ├── labels.py      # Label commands
│   ├── sections.py    # Section commands
│   ├── comments.py    # Comment commands
│   ├── config_cmd.py  # td init, td completions
│   ├── rate_limit.py  # td rate-limit display
│   ├── review.py      # td review (interactive TUI)
│   ├── schema_cmd.py  # td schema (capability manifest)
│   ├── output.py      # OutputFormatter — Rich/JSON/Plain modes
│   ├── completions.py # Shell completion generation
│   └── errors.py      # Structured TdError handling
├── tui/           # Optional interactive UI (requires textual)
│   ├── picker.py      # Interactive task picker
│   ├── pickers.py     # Multi-picker utilities
│   └── review.py      # Interactive inbox review
└── schema.py      # Click command tree → JSON schema
```

**Key principle:** `core/` is a standalone library. `cli/` is a thin wrapper. Never import from `cli/` in `core/`.

## Tech Stack

- **CLI framework:** Click (not Typer — we own output/schema/completions)
- **API client:** todoist-api-python (REST API v2)
- **Output:** Rich (tables, colors), with JSON and plain-text fallbacks
- **Config:** TOML files at `~/.config/td/config.toml` (XDG-compliant)
- **Interactive TUI:** Textual (optional `[interactive]` extra)
- **Linting:** ruff (E, F, W, I, UP, B, SIM, RUF rules, line-length 99)
- **Types:** mypy --strict (Python 3.10 target)
- **Tests:** pytest + pytest-cov (85% minimum), pytest-mock, pytest-asyncio
- **Docs:** mkdocs-material + mkdocs-click

## Critical Patterns

### Priority mapping (gotcha)

Todoist API uses **inverted** priority numbers: API `4` = urgent, API `1` = low.
Display labels are the opposite: `p1` = urgent, `p4` = low.
Conversion: `display = 5 - api_priority`. Always use this formula — never assume p1 means API 1.

### Task reference resolution

Commands like `done`, `edit`, `show`, `delete` accept flexible task references, resolved in order:
1. **Row number** — digits checked against cached result from last `td ls`/`td today` (10 min TTL)
2. **Content match** — fuzzy substring match if text and `len > 2` (interactive picker if ambiguous in TTY)
3. **Task ID** — raw passthrough as Todoist task ID

This is implemented in `cli/tasks.py:_resolve_task()` using `core/cache.py:resolve_task_ref()`.

### Output formatter

Every command accesses the formatter via `ctx.obj["formatter"]` (helper: `_get_formatter(ctx)`).
All JSON output is wrapped in an envelope: `{"ok": true, "type": "<result_type>", "data": ...}`.
Errors go to stderr in the same format: `{"ok": false, "error": {"code": "...", ...}}`.

Output mode resolution order (most specific wins):
1. `--json` / `--plain` flags
2. `default_format` from config
3. `NO_COLOR` / `color` setting
4. TTY detection (TTY → Rich, pipe → JSON)

### Error handling

All errors are `TdError` subclasses (in `cli/errors.py`) with `code`, `message`, `suggestion`.
The `TdGroup.invoke()` in `cli/__init__.py` catches all exceptions — `TdError` directly, other
exceptions via `map_api_exception()` which maps HTTP status codes to structured errors.

### Cache system

Two caches in `~/.cache/td/` (respects `XDG_CACHE_HOME`):
- `last_results.json` — row-number-to-task-ID mapping from last list command (10 min TTL)
- `names.json` — project/label/section name mappings (5 min TTL)

TTLs are currently hardcoded (see issue #127).

### Command registration

Commands are registered via lazy imports in `_register_commands()` at module level in
`cli/__init__.py`. This avoids circular imports. New commands must be both imported AND
added via `cli.add_command()`.

### Python compatibility

All modules use `from __future__ import annotations` for Python 3.10 compatibility with
modern type syntax (e.g., `str | None`).

## Code Style

- Full type annotations everywhere — `mypy --strict` must pass
- All commands use `OutputFormatter` for Rich/JSON/Plain output
- All errors use structured `TdError` subclasses with codes and suggestions
- TTY-aware: pretty tables for humans, JSON when piped
- Coverage excludes `tui/` and `cli/review.py` (interactive code)

## Commit Conventions

Conventional Commits: `<type>(<scope>): <description>`

- **Types:** feat, fix, docs, refactor, test, ci, chore
- **Scopes (optional):** tasks, output, errors, config, core, ci, deps
- **Branches:** `feat/description`, `fix/description`, `docs/description`

## Adding a New Command

1. Business logic in `td/core/<module>.py`
2. Click command in `td/cli/<module>.py`
3. Register in `td/cli/__init__.py`
4. Add output methods to `td/cli/output.py` if needed
5. Add tests in `tests/`
6. Update schema test expected commands set
7. Verify with `td schema`

## Development Workflow

See [CONTRIBUTING.md](CONTRIBUTING.md) for the full workflow: issue tracking, milestones,
branching, changelog conventions, versioning, and release process. AI assistants should
follow the same process — the conventions apply equally.

## Testing

```bash
make test                        # Full suite with coverage
pytest tests/test_tasks.py       # Single test file
pytest tests/test_tasks.py -k "test_sort"  # Single test by name
```

- Tests mock `TodoistAPI` — no real API calls in the test suite
- `conftest.py` has an autouse fixture that isolates cache via `XDG_CACHE_HOME` → tmp_path
- CLI tests use Click's `CliRunner` for invocation testing
- Coverage minimum is 85%, enforced by `--cov-fail-under=85`

## Known Architectural Issues

- `core/client.py` defines its own `TdAuthError` (plain Exception), separate from
  `cli/errors.py`'s `TdAuthError` (TdError subclass) — issue #125, a layering violation
- Cache TTLs (10 min results, 5 min names) are hardcoded — issue #127
- Some SDK type mismatches suppressed with `type: ignore` — issue #129

## Environment Variables

- `TD_API_TOKEN` — API auth (preferred for agents/CI)
- `TD_CONFIG_DIR` — Override config directory
- `TD_DEBUG` — Enable debug logging
- `NO_COLOR` — Disable colored output

## CI

- Lint on Python 3.13 (Ubuntu)
- Tests on Python 3.10–3.13 x Ubuntu + macOS
- Coverage uploaded to Codecov from Ubuntu 3.13 run
- Pre-commit hooks: ruff check (auto-fix) + ruff format

## Entry Point

`td = "td.cli:main"` (defined in pyproject.toml)
