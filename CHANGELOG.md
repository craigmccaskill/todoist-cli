# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

<<<<<<< HEAD
### Internal
- Add pytest-timeout (30s per test) and CI job timeouts to prevent hanging tests (#140)
- Add dependency vulnerability scanning with pip-audit in CI and `make audit` locally (#146)
- Enhance PR template with CONTRIBUTING.md workflow checklist and consolidate feature templates (#148)
### Fixed
- `td init` no longer exposes API token in shell history when choosing environment variable storage (#138)
=======
>>>>>>> c89bdc6 (fix(tui): implement filter, undo, and fix keyboard shortcuts in TUI components)
### Changed
- Fix TUI keyboard shortcuts: implement `/` filter in picker, real undo in review, modal Enter binding, standardize hints (#117)
- Audit and improve table columns across all list views (#112)
  - Task list plain mode now matches Rich column order: #, PRI, CONTENT, PROJECT, DUE, LABELS
  - Smart column hiding in plain mode: PROJECT and LABELS columns auto-hide when not applicable
  - Project list: consistent NAME, ★, ID order with favorite indicator in plain mode
  - Label list: `@` prefix in plain mode to match Rich
  - Section list: NAME, ID order in plain mode (was ID, NAME)
  - Comment rendering moved into `OutputFormatter.comment_list()` with human-readable timestamps
  - Overdue due dates styled red (was yellow) in Rich task tables
  - Empty list states show helpful messages instead of empty tables
  - `search` and `log` commands now include project name column
- Full UX review: improved help text, documented defaults, consistent flag descriptions, cleaner error messages (#122)

### Fixed
- TUI `RowKey` resolution: use `row_key.value` instead of `str(row_key)` for Textual 8.x compatibility in picker and review modal screens (#159)

### Internal
- Comprehensive Textual pilot tests for all TUI components: PickerApp, filter, domain pickers, modal screens, and ReviewApp actions (58 tests) (#159)

## [0.8.0-alpha] - 2026-04-04

### Added
- `--id` flag on `done`, `edit`, `show`, `delete`, `move`, `undo` to bypass task reference resolution and use literal task IDs (#128)

### Fixed
- Rate limit monitoring never captured data — rewritten from `requests.Session` to `httpx.Client` event hooks to match SDK's HTTP stack (#119)
- Cache file writes are now atomic via temp file + `os.rename()`, preventing corruption from concurrent invocations or Ctrl+C (#152)
- Config file written with default permissions (world-readable) — now sets `0o600` on file, `0o700` on directory (#137)
- `py.typed` marker declared in package data so it ships in wheels (#139)
- SDK `type: ignore[arg-type]` suppressions replaced with named parameters for full mypy coverage at API boundaries (#129)
- Formatter access `type: ignore[no-any-return]` replaced with `cast()` across all CLI modules (#129)
- Invalid `default_command` in config silently exited 0 — now errors with exit code 1 and lists valid commands (#155)
- Invalid `default_format` and `default_sort` in config now warn on stderr and fall back to defaults (#153)

### Changed
- Core exceptions moved to `core/exceptions.py` — `core/` no longer imports from `cli/`, enabling standalone library use (#125, #136)
- Broad `except Exception` in cache operations narrowed to specific types with debug logging (#126, #141)
- `todoist-api-python` constraint bumped from `<4` to `<5`; `requests` dependency dropped in favor of `httpx` (#135)

### Internal
- CI: added `cache: 'pip'` to all `setup-python` steps for faster workflow runs (#145)
- Tier 3 architectural test: `core/` never imports from `cli/` (#125)
- Regression test: unexpected exceptions propagate from narrowed cache catches (#126)

## [0.7.0-alpha] - 2026-03-25

### Added
- Dynamic shell completions for project, label, and section names (#24)
- Documentation site with mkdocs-material — deployed to GitHub Pages (#38)
- `make docs` for local documentation preview

## [0.6.0-alpha] - 2026-03-25

### Added
- `td review` — interactive TUI for inbox processing with j/k navigation and action keybindings (#101)
- Interactive task picker for commands called with no arguments in TTY mode (#101)
- `textual` added as optional dependency: `pip install todoist-cli[interactive]`
- TUI picker infrastructure: reusable table/picker widgets in `src/td/tui/`
- Modal picker screens for project, priority, and label selection in review mode
- Shortcut bar toggle (h) and help screen (?) in review TUI

## [0.5.0-alpha] - 2026-03-25

### Added
- `td show <ref>` — view full task details with panel layout (#65)
- `td search <query>` — full-text search across all tasks (#75)
- `td move <ref> -p <project>` — move tasks between projects (#66)
- `td comment <ref> <text>` — add comments to tasks (#72)
- `td comments <ref>` — list comments on a task (#72)
- `td rate-limit` — show API rate limit status from cached headers (#78)
- `td add --section` flag to place tasks in a specific section (#76)
- `td` with no subcommand runs default command (configurable, defaults to `today`) (#74)
- Project name column in `td ls` and `td today` output (#64)
- Confirmation prompt on fuzzy match `td done` in TTY mode (#73)
- Rate limit monitoring via `requests.Session` response hooks — warns to stderr at 80% usage (#78)
- `merge_group` CI trigger for future merge queue support (#87)

### Changed
- README install instructions updated to reflect current state (clone from source) (#94)

## [0.4.0-alpha] - 2026-03-25

### Added
- `td section-add <name> -p <project>` — create sections from the CLI (#77)
- `td label-add <name>` — create labels from the CLI (#77)
- `td edit <ref>` with no flags now shows current task values (#67)
- Example generator covers all 22 commands (#69)

### Changed
- Migrated to `src/` layout for proper test isolation (#37)
- CI lint job uses `make lint` instead of separate tool installs (#71)
- `make release` creates a branch + PR instead of pushing directly to main (#68)
- Auto-delete head branches on merge enabled (#70)

## [0.3.0-alpha] - 2026-03-24

### Added
- Fuzzy content matching — `td done milk` finds and completes matching task (#13)
- Natural language refs without quotes — `td done buy milk`, `td edit blog post --due friday`
- Resolution chain: row number → content match → task ID on all task commands
- Interactive picker when multiple tasks match (TTY), structured error (non-TTY)

### Changed
- `task_id` argument replaced with `task_ref` (nargs=-1) on done, undo, edit, delete

## [0.2.0-alpha] - 2026-03-24

### Added
- `td capture` — minimal-friction inbox append, no parsing (#32)
- `td today` — morning dashboard: overdue + due today (#7)
- `td next` — show highest priority task (#8)
- `td log` — completed tasks today or `--week` (#10)
- `td focus <project>` — single-project deep work view (#11)
- `td project-add` — create projects from the CLI
- `td undo` — reopen completed tasks (#16)
- Numbered results — `td ls` shows row numbers, `td done 1` works (#12)
- `--sort` and `--reverse` flags on list commands (#48)
- `--ids` flag on `td ls` for Unix piping (#23)
- `--debug` flag for API troubleshooting (#44)
- Stdin piping for `td add` and `td quick` (#31, #21)
- Name caching with 5-min TTL for project/label/section resolution (#28)
- Result caching for numbered row references (10-min TTL)
- Interactive `td init` — choose config file or env var (#19)
- Configurable default output format via `TD_FORMAT` env or config (#20)
- Configurable default sort via `TD_SORT` env or config
- Smart `td ls` default — shows today + overdue, `--all` for everything (#17)
- `-h` shorthand for `--help` on all commands
- `SECURITY.md` vulnerability reporting policy (#34)
- Coverage gate at 85% in CI (#36)
- `Makefile` with dev workflow commands (#40)
- Separate dependency groups in pyproject.toml (#39)
- Conventional commits guide in CONTRIBUTING.md
- `make release` workflow for versioning
- Branch protection on main
- Feature spec issue template

### Changed
- Priority help text now reads "1=urgent, 2=high, 3=medium, 4=low" (#18)

## [0.1.0-alpha] - 2026-03-24

### Added
- Task commands: `add`, `ls`, `done`, `edit`, `delete`, `quick`, `inbox`
- Organization: `projects`, `sections`, `labels`
- AI-native: `schema` capability manifest, structured JSON errors, TTY-aware output
- `--idempotent` flag on `td add` to prevent duplicate creation
- `--json`, `--plain` flags on all commands
- `td init` for interactive auth setup
- `td completions` for bash/zsh/fish shell completions
- Config at `~/.config/td/config.toml` (respects `XDG_CONFIG_HOME`, `TD_CONFIG_DIR`)
- `NO_COLOR` support
- CI: multi-OS (ubuntu + macOS), multi-Python (3.10–3.13)
- Release workflow: build + publish to PyPI on tag
- Pre-commit hooks, dependabot, issue/PR templates
- CONTRIBUTING.md, AGENTS.md
- Example output documentation at `docs/examples.md` with generator script
