# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

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
