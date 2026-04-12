# CLAUDE.md — Project context for AI assistants

## About this file

Loaded at the start of every session. Content must pass the
*catastrophic-omission test*: would its absence cause high-cost rework
that no other mechanism catches? Frequency of relevance is not the
test; consequences of failure are.

- Max 3 tier-1 principles at any time
- Task-specific guidance lives in scoped subsections, not at the top
  level
- Content is removed when a stronger mechanism (CI check, linter,
  architectural test) replaces it

## What is this?

`td` — an AI-native Todoist CLI built for humans and AI agents. Python 3.10+, alpha (v0.12.0-alpha).

## Quick Reference

```bash
make check      # Run lint + tests (the one command before committing)
make fmt        # Auto-format code
make test       # Tests only (pytest, 85% coverage minimum)
make lint       # ruff check + ruff format --check + mypy strict
make audit      # Scan dependencies for known vulnerabilities (pip-audit)
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
- **Tests:** pytest + pytest-cov (85% minimum), pytest-mock, pytest-asyncio, pytest-timeout (30s)
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

**Output consistency principle:** Rich and Plain modes must use the same column order for
all list views. Smart column hiding (e.g., omitting PROJECT in inbox view) applies to both
modes. Empty lists show a helpful message ("No tasks found.") instead of an empty table.
Overdue dates are styled red; non-overdue dates are yellow.

### Error handling

All errors are `TdError` subclasses (in `cli/errors.py`) with `code`, `message`, `suggestion`.
The `TdGroup.invoke()` in `cli/__init__.py` catches all exceptions — `TdError` directly, other
exceptions via `map_api_exception()` which maps HTTP status codes to structured errors.

### Cache system

Two caches in `~/.cache/td/` (respects `XDG_CACHE_HOME`):
- `last_results.json` — row-number-to-task-ID mapping from last list command (10 min TTL)
- `names.json` — project/label/section name mappings (5 min TTL)

TTLs are configurable via `cache_ttl_results` and `cache_ttl_names` in `config.toml` (defaults: 600s and 300s).

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

## Adding a New Command or Changing Output Shape

Before writing code, the work must conform to the design principle
(ADR-0001):

- **Accept what the user means, not what the system needs.** The
  common case should be flag-free. Flags are for disambiguation.
- **Show what's useful, not what the API returns.** Tables show rows,
  names, and dates, not opaque IDs. Empty states explain what to do
  next.
- **Help the user recover when things go wrong.** Every error answers
  what happened, why, and what to do next. Ambiguous input triggers a
  picker, not a failure.
- **Progressive disclosure.** The simple case stays simple. Power
  features exist but stay out of the way.

For full rationale, read
[docs/decisions/0001-design-principle.md](docs/decisions/0001-design-principle.md).
For other ADRs that may apply, check
[docs/decisions/README.md](docs/decisions/README.md).

### Default to plan mode for feature work

Before writing any code for changes in the `feat(tasks|output|cli)`
conventional-commit scopes, enter plan mode. Explore the relevant
code (read-only), form a concrete implementation plan, and exit plan
mode only once the plan is written and reviewed. Do not skip planning
because the task *"looks simple"*. These scopes are where design
decisions live, and the cost of shipping a wrong command design is a
retroactive redesign under the ADR process.

Out of scope: `fix(*)`, `docs`, `ci`, `chore`, and refactors that do
not change observable behavior. Plan mode for those is optional and
should not become a default tax.

### Research-before-implement for delegated work

When delegating implementation work to a background agent via the
Agent tool for changes that add a new command, modify output shape,
or touch an architectural invariant, spawn a **Plan agent first** to
do research. Review the Plan agent's output before spawning the
implementation agent.

**Plan agent prompt template:**

    Research task for #<issue>. Do NOT write code.

    1. Read docs/decisions/README.md and identify ADRs that apply
       to this work
    2. Read the relevant ADRs in full (especially ADR-0001)
    3. Read existing commands in the same area
       (e.g. src/td/cli/tasks.py) to understand current patterns

    Output a proposal with:

    - Which ADRs apply and what they constrain
    - Existing patterns to reuse (with file paths)
    - Two or three alternative approaches with tradeoffs
    - Recommended approach with rationale
    - Open questions that need user decisions before implementation

    Keep the output under 500 words.

Only after reviewing the research output and resolving any open
questions should you spawn the implementation agent, passing the
approved approach and a reference to the research findings. This is
the pattern that catches the #250 class of failure: a Plan agent
that reads ADR-0001 before any implementation exists will flag
design-principle violations before code is written.

### Mechanical checklist

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

### Textual 8.x gotcha

In Textual 8.x, `DataTable.coordinate_to_cell_key()` returns a `RowKey` object. Use
`row_key.value` to get the actual key string — `str(row_key)` returns the Python repr,
not the key. This affects `PickerApp.action_select()`, `ReviewApp._get_selected_task()`,
and all modal `action_select()` methods.

## Environment Variables

- `TD_API_TOKEN` — API auth (preferred for agents/CI)
- `TD_CONFIG_DIR` — Override config directory
- `TD_DEBUG` — Enable debug logging
- `NO_COLOR` — Disable colored output

## CI

- Lint on Python 3.13 (Ubuntu)
- Tests on Python 3.10–3.13 x Ubuntu + macOS (30s per-test timeout, 20min job timeout)
- Security: pip-audit vulnerability scanning on every push/PR
- Packaging: build sdist/wheel + smoke-test installs (td --version, td schema, py.typed)
- Dependency Review: GitHub advisory comments on PRs that change dependencies
- Coverage uploaded to Codecov from Ubuntu 3.13 run
- Pre-commit hooks: ruff check (auto-fix) + ruff format

## Entry Point

`td = "td.cli:main"` (defined in pyproject.toml)
