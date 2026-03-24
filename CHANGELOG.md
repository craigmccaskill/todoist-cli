# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.1.0-alpha] - 2026-03-24

### Added
- Task commands: `add`, `ls`, `done`, `undo`, `edit`, `delete`, `quick`, `inbox`
- Workflow commands: `today`, `next`, `log`, `focus`
- Organization: `projects`, `project-add`, `sections`, `labels`
- AI-native: `schema` capability manifest, structured JSON errors, TTY-aware output
- `--idempotent` flag on `td add` to prevent duplicate creation
- `--json`, `--plain` flags on all commands
- `--sort` and `--reverse` flags on list commands (priority, due, project, created)
- `--ids` flag on `td ls` for Unix piping
- `--all` flag on `td ls` (default is today + overdue)
- `-h` shorthand for `--help` on all commands
- Configurable default output format (`TD_FORMAT` env, `default_format` in config)
- Configurable default sort (`TD_SORT` env, `default_sort` in config)
- `td init` for interactive auth setup
- `td completions` for bash/zsh/fish shell completions
- Shell completion generation via Click's `_TD_COMPLETE` mechanism
- Config at `~/.config/td/config.toml` (respects `XDG_CONFIG_HOME`, `TD_CONFIG_DIR`)
- `NO_COLOR` support
- CI: multi-OS (ubuntu + macOS), multi-Python (3.10–3.13), coverage gate at 85%
- Release workflow: build + publish to PyPI on tag
- Pre-commit hooks, dependabot, issue/PR templates
- SECURITY.md, CONTRIBUTING.md, AGENTS.md
- `Makefile` with `make check`, `make test`, `make lint`, `make fmt`, `make release`
- Example output documentation at `docs/examples.md` with generator script
