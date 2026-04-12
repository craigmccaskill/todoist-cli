# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Internal

- **Project board conventions codified and board restructured** — field definitions and dependency tracking now documented in `CONTRIBUTING.md`, with the GitHub Project updated to match.
  - **New `Tier` field** added to the project with five values: `Needs triage` (default), `Trivial`, `Standard`, `Needs ADR`, `Exploratory`. Captures the pre-work ritual each issue needs.
  - **`Status` restructured.** Added `Ready`, `In flight`, and `Blocked`. Removed dead `Sprint` and `In Progress` options.
  - **`AI Platform` theme removed.** The two affected items (#15 Natural language actions and #27 MCP server mode) were bumped to `P1` and left without a theme (to be retagged during re-triage).
  - **`Priority` gains explicit definitions** (`P0` through `P3`) in `CONTRIBUTING.md` without any renaming or retagging.
  - **Triage decision framework** captured in ADR-0010. Checklist-style rubric walked for every issue leaving `Needs triage`. Classifies `Tier`, `Size`, `Priority` with worked examples and edge cases. No automation in v1 (rubric discipline only).
  - **Dependency tracking convention documented** (captured in ADR-0011). Hierarchical via GitHub task lists, cross-cutting via `Blocks:` / `Blocked by:` keywords in the issue body.
  - **Board transitions automated via native Projects v2 workflows.** Merging a PR moves the linked issue's `Status` to `Done`; opening a PR with `Closes #N` moves the linked issue to `In flight`. Both run on GitHub's built-in Projects v2 workflows (`Pull request merged` and `Pull request linked to issue`). No PAT, GitHub App, or repo secret required. Rules documented in the Branch → PR → Merge section of `CONTRIBUTING.md`.

- **Architecture Decision Records** — design decisions now have a durable home in `docs/decisions/` (#224). Eight retroactive ADRs capture decisions already baked into the code: design principle (#230), JSON output envelope, priority mapping, task reference resolution order, `core/`/`cli/` boundary, schema as AI contract, cache TTLs, and Click-over-Typer.
  ```
  # Citeable from PRs and commits
  "implements ADR-0003"
  "diverges from ADR-0001, see new ADR-0009"
  ```
  ADRs use the Nygard template (one page, immutable once accepted, superseded rather than edited). The directory is indexed at `docs/decisions/README.md` and rendered in the docs site under "Design Decisions".

  ADR-0001 (Design Principle) explicitly captures a **CLI surface boundary** rule: the `td` public command tree is reserved for end users of Todoist. Project maintenance tooling (triage helpers, release scripts, dependency audits, contributor onboarding, etc.) does not ship in the public CLI. Maintainer tooling lives in Claude skills, GitHub Actions, or scripts under `.github/` or `scripts/`. The rule is reinforced by a matching checklist item in `CONTRIBUTING.md`'s "Adding a New Command" section.

- **`CLAUDE.md` scoped for attention routing** — new "About this file" meta-section establishes the *catastrophic-omission test* for what belongs in the file (content whose absence causes high-cost rework that no other mechanism catches, capped at three tier-1 principles at a time). The existing "Adding a New Command" section is replaced with "Adding a New Command or Changing Output Shape", carrying a 4-bullet summary of the design principle plus pointers to ADR-0001 and the decisions index. Agents see the principle *before* writing code, not after shipping against it — the failure mode that produced #250.

- **`CONTRIBUTING.md` restructured to prevent the #250 pattern**
  - Design Principle section now references ADR-0001 as the canonical version
  - New Architecture Decision Records section documenting when an ADR is required (new command grammar, output envelope changes, new architectural invariants, supersessions)
  - Milestones section gains a **Batch anti-patterns** callout addressing the specific failure modes that produced #250: rolling multiple design decisions into one batch issue, dumping 20 issues into a milestone in 20 minutes, treating dashboard progress as a forcing function, heterogeneous work in one milestone
  - "Before starting work" is now **tiered** — Trivial / Standard / Design-affecting — with different pre-work rituals per tier, so a typo fix and a 10-command CRUD surface no longer get the same ceremony
  - Size triggers (>200 lines or >3 modules) bump work out of the Trivial tier and force explicit consideration of whether it crosses into Design-affecting
  - "Adding a New Command" checklist gains an explicit ADR check as its final item

- **Docs site** gains a "Design Decisions" nav section listing all eight retroactive ADRs. `docs/contributing.md` gains minimal pointers to the design principle and `docs/decisions/` for discoverability from the public docs.

## [0.12.0-alpha] - 2026-04-09

### Added

- **Time-based views** — plan ahead without filter syntax (#211)
  ```bash
  td tomorrow              # due tomorrow
  td upcoming              # next 7 days
  td upcoming 3            # next 3 days
  td overdue               # just overdue, without today mixed in
  td overdue Work          # overdue in one project
  ```

- **`td skill install`** — auto-generate a command reference for AI agents (#214)
  ```bash
  td skill install         # auto-detects Claude Code
  td skill                 # shows status, warns if stale after update
  td skill update          # regenerate with latest commands
  ```
  SKILL.md includes full command reference, agent guidance, and security notes.
  Version tracking shows when the skill file is stale.

- **Positional args for `td completed`** — no more `--since "7 days"` (#243)
  ```bash
  td completed 7d          # last 7 days
  td completed Work 2w     # last 2 weeks in Work
  td completed 2026-04-01  # since a date
  ```
  Duration and project are auto-classified. Order doesn't matter.

### Changed

- **README rewritten** — leads with a morning workflow, not a feature list. Drops command table and architecture diagram. (#189)

- **examples.md rewritten** — narrative workday guide instead of auto-generated command reference (#186)

### Fixed

- **Task refs validate before hitting the API** — `td done ljasdf` now shows "Task not found" with a suggestion instead of a raw `400 Bad Request` (#242)

## [0.11.0-alpha] - 2026-04-09

### Added

- **Unified `td add`** — one command that does the right thing (#192)
  ```bash
  td add buy milk tomorrow        # human at keyboard: NLP parses it
  td add "Deploy" --due Friday    # explicit flags: literal mode
  echo "idea" | td add            # piped input: literal mode
  ```
  `td quick` and `td capture` still work as hidden aliases with a deprecation notice.

- **`td completed`** — see what you've done (#210)
  ```bash
  td completed                    # completed today
  td completed --since "7 days"   # last week
  td completed Work               # scoped to a project
  ```

- **`td doctor`** — diagnose your setup in one command (#213)
  ```bash
  td doctor
  ✓ Python 3.12
  ✓ Config file valid
  ✓ API token present
  ✓ API connection OK (3 projects)
  ✗ Shell completions: not installed
  ```

- **Full CRUD for projects, sections, labels, and comments** (#217)
  ```bash
  td project-edit Work --name "Work stuff"
  td project-delete "Old Project" -y
  td project-archive Done
  td section-delete Backlog -y
  td label-edit urgent --name critical
  td comment-delete c123 -y
  ```
  All destructive commands require `-y` or confirmation.

- **`td completions install`** — one command to enable tab completion (#229)
  ```bash
  td completions              # show status
  td completions install      # add to your shell profile
  td completions uninstall    # remove it
  ```
  `td init` now offers to set up completions automatically.

- **PATH collision detection** — `td init` warns if another `td` is on your PATH (#208)

### Changed

- **Design principle documented** — "surface the context users need to be successful, nothing more" now guides all UX decisions (#230)

- **Tables show useful data, not raw IDs** — projects, sections, labels, and comments no longer display opaque IDs in Rich/Plain output. IDs remain in JSON for scripting. (#231)

- **pip install from git URLs works** — version resolution fixed for blobless clones (#228)

### Fixed

- **Comprehensive error audit** — every HTTP status code, network timeout, corrupt cache, and invalid config now produces a human-readable message with an actionable suggestion (#227)

### Internal

- Updated CLAUDE.md for v0.10.0 changes (#209)

## [0.10.0-alpha] - 2026-04-09

### Added

- **Batch task completion** — knock out multiple tasks in one command (#194)
  ```
  td done 2 4        # complete rows 2 and 4 from your last td ls
  ```
  Each task is completed independently. If one fails, the rest still go through
  and you'll see which ones failed.

- **List all sections at a glance** — `td sections` no longer requires `-p` (#120)
  ```
  td sections          # all sections, grouped by project
  td sections -p Work  # still works for a single project
  ```

- **Shell auto-detection for completions** — no more guessing (#121)
  ```
  td completions       # detects zsh/bash/fish from $SHELL
  td completions zsh   # explicit override still works
  ```

- **Configurable cache TTLs** — tune how long row numbers and name lookups stay fresh (#127)
  ```toml
  # ~/.config/td/config.toml
  [settings]
  cache_ttl_results = 120   # row number cache (default: 600s)
  cache_ttl_names = 60      # project/label/section cache (default: 300s)
  ```

### Changed

- **Priority column is now accessible** — single column with colored bar + uncolored label (#130)
  ```
  Before:  ▎  p1   Fix bug      (two columns, both colored)
  After:   ▎ p1    Fix bug      (one column, label readable without color)
  ```
  The colored bar provides visual priority at a glance. The uncolored text label
  ensures priority is readable for colorblind users and in plain terminals.

### Fixed

- **Error messages are human-readable** — no more raw `400 Bad Request` (#195)
  ```
  Before:  Error: API error: 400 Bad Request
  After:   Error: Bad request: Invalid due date
           Suggestion: Check command arguments. Use --help for usage details.
  ```
  The CLI now extracts error details from API responses and includes actionable
  suggestions for all error types.

- **Empty search queries caught before hitting the API** — `td search ""` now returns a clear validation error instead of sending a malformed query (#154)

- **Config round-trip preserves your custom fields** — manually added TOML keys and sections are no longer silently dropped when td writes to config.toml (#143)

- **Debug logging actually works now** — `TD_DEBUG=1` enables the `td` package logger and uses `httpx`/`httpcore` (matching the actual HTTP stack) instead of the unused `urllib3` logger (#156)

## [0.9.0-alpha] - 2026-04-05

### Changed
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
- Fix TUI keyboard shortcuts: implement `/` filter in picker, real undo in review, modal Enter binding, standardize hints (#117)
- `td init` now shows clickable Todoist settings URL, trust-building helper text, and specific error messages for auth failures, network issues, and rate limits (#107)

### Fixed
- `td init` no longer exposes API token in shell history when choosing environment variable storage (#138)
- TUI `RowKey` resolution: use `row_key.value` instead of `str(row_key)` for Textual 8.x compatibility in picker and review modal screens (#159)

### Internal
- Add pytest-timeout (30s per test) and CI job timeouts to prevent hanging tests (#140)
- Add dependency vulnerability scanning with pip-audit in CI and `make audit` locally (#146)
- Add CI packaging verification — build sdist/wheel and smoke-test installs on every push/PR (#150)
- Enhance PR template with CONTRIBUTING.md workflow checklist and consolidate feature templates (#148)
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
