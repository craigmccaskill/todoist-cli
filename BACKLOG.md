# Backlog

Prioritized list of features and improvements beyond the Tier 1 MVP.

## Tier 2 — Workflow & Differentiation

### Opinionated Workflow Commands
- [ ] `td today` — Start-of-day dashboard: overdue + due today, grouped by project
- [ ] `td next` — Show highest priority task across all projects ("what should I work on?")
- [ ] `td review` — Interactive inbox processing: show each inbox task one at a time, assign project/priority/due or snooze
- [ ] `td log` — End-of-day review: show tasks completed today/this week
- [ ] `td focus <project>` — Show only tasks for one project, sorted by priority

### UX Improvements
- [ ] `td undo <id>` — Uncomplete a task (SDK has `uncomplete_task()`)
- [ ] Change `td ls` default to show today + overdue only (add `--all` for everything)
- [ ] Document priority mapping clearly (user-facing: 1=urgent, API: 4=urgent) in help text and README
- [ ] Reconsider priority display in plain mode — `p1`/`p4` is confusing vs Todoist's native numbering
- [ ] `td init` should be interactive: ask whether to store token in `~/.config/td/config.toml` or suggest adding to shell env file (`.env`, `.bashrc`, etc.)
- [ ] Configurable default output mode — `default_format` in config.toml (`rich`, `plain`, `json`). Lets users/agents set their preferred default without flags on every command. Also respect `TD_FORMAT` env var for per-session override

### Power Features (from original brief)
- [ ] `td quick` improvements — already in Tier 1, but could add `td quick` with stdin pipe support
- [ ] `td interactive` / `td i` — TUI for reviewing/processing inbox (rich or textual)
- [ ] Bulk operations via piping (`td ls --filter "today & #Errands" --ids | xargs -I {} td done {}`)
- [ ] `--ids` flag on `td ls` — output only task IDs, one per line, for piping
- [ ] Dynamic shell completions (tab-complete project and label names from API)
- [ ] `td sync` — Local cache for offline list viewing
- [ ] Templates — `td add --template daily-standup`
- [ ] MCP server mode — `td serve --mcp` exposes same logic over MCP protocol
- [ ] Project/section name caching with configurable TTL

## Tier 3 — Ecosystem

- [ ] Obsidian bridge/plugin
- [ ] GitHub Actions support (CI task creation)
- [ ] stdin piping for `td add` (capture from anywhere)
- [ ] `td capture` — Minimal-friction append to inbox, designed for shell aliases/hotkeys
- [ ] Plugin system for custom output formatters

## Quality & Infrastructure (from comparison with top CLI tools)

### High Priority
- [ ] `SECURITY.md` — Vulnerability reporting policy
- [ ] Demo GIF/recording using vhs or asciinema for README
- [ ] Coverage threshold in CI (`--cov-fail-under=85`)
- [ ] `src/` layout migration (Click, Black use this — better test isolation)

### Medium Priority
- [ ] Documentation site with mkdocs-material, deployed to GitHub Pages
  - Getting started guide
  - Configuration reference
  - AI/agent integration guide
  - Design patterns post (reusable content for blog)
- [ ] Separate `[project.optional-dependencies]` groups: `test`, `docs`, `dev`
- [ ] `Makefile` or `justfile` with common dev commands (`make test`, `make lint`, `make docs`)

### Lower Priority
- [ ] Homebrew formula for macOS install
- [ ] Docker image for CI/container usage
- [ ] Fuzzing / property-based tests (hypothesis)
- [ ] Benchmark workflow for API response time tracking
- [ ] `--verbose` / `--debug` flag for troubleshooting API issues
