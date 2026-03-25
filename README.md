# td — AI-Native Todoist CLI

[![CI](https://github.com/craigmccaskill/todoist-cli/actions/workflows/ci.yml/badge.svg)](https://github.com/craigmccaskill/todoist-cli/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

> A modern Todoist CLI built on REST API v2, designed for both humans and AI agents.

**Status:** Alpha — feature-complete for core task management. [See the roadmap.](https://github.com/users/craigmccaskill/projects/1)

![td demo](docs/demo/demo.gif)

## Features

- **TTY-aware everything** — pretty Rich tables for humans, structured JSON when piped. Errors, output, and pickers all adapt automatically. No flags needed.
- **Interactive TUI** — `td review` opens a full inbox-processing interface with keyboard navigation. Commands like `td done` launch a task picker when called with no args. Install `todoist-cli[interactive]` to enable.
- **Fuzzy task matching** — `td done buy milk` finds and completes the right task. Confirms before acting on ambiguous matches.
- **Capability manifest** — `td schema` dumps every command, argument, and option as JSON. An agent calls it once and knows everything.
- **TTY-aware errors** — styled messages with actionable suggestions for humans, structured JSON with error codes for agents. Same error, two formats, zero config.
- **Idempotent operations** — `--idempotent` flag prevents duplicate task creation, solving the #1 agent failure mode.
- **Natural language input** — `td quick "Buy milk tomorrow p1 #Errands"` parsed by Todoist's engine.
- **Rate limit awareness** — monitors API usage in the background, warns before you hit the limit, `td rate-limit` shows current status without an API call.
- **Library-first architecture** — CLI and [planned MCP server](https://github.com/craigmccaskill/todoist-cli/issues/27) are thin frontends over the same tested core.
- **MCP alternative** — same task management capabilities without the auth flakiness and token overhead of existing MCP integrations.

## Install

```bash
git clone https://github.com/craigmccaskill/todoist-cli.git
cd todoist-cli
pip install -e .
```

Requires Python 3.10+. PyPI package coming soon.

## Quick Start

```bash
# Set up authentication
td init

# Add a task (priority: 1=urgent, 2=high, 3=medium, 4=low)
td add "Review PR for auth module" -p Work --priority 1 -d tomorrow

# Natural language quick add
td quick "Buy milk tomorrow p2 #Errands"

# List tasks (defaults to today + overdue)
td ls
td ls --all                  # everything
td ls -p Work --sort due     # sorted by due date
td ls -f "today & #Work"

# Morning dashboard / what to work on next
td today
td next

# Quick capture to inbox — no parsing, no flags
td capture call dentist about appointment

# Complete a task (row number, content match, or ID — no quotes needed)
td done 1
td done buy milk
td done 8bx9a0c2

# Reopen a completed task
td undo <task-id>

# Edit a task
td edit <task-id> --due "next monday"

# Delete a task
td delete <task-id>
```

## AI / Agent Usage

td is built for AI agents as a first-class use case — and a lightweight alternative to MCP for Todoist integration.

### Why not MCP?

MCP servers for Todoist exist, but they suffer from auth flakiness, excessive token consumption, and opaque error handling. td gives agents the same capabilities through a simpler interface: structured JSON over stdout/stderr, a self-describing schema, and idempotent operations. No persistent connection, no protocol overhead.

An [MCP server mode](https://github.com/craigmccaskill/todoist-cli/issues/27) is planned as a thin frontend over the same core — giving you both options from one tool.

### Automatic JSON output

When stdout is not a TTY (i.e., piped or called by an agent), td outputs structured JSON automatically:

```bash
# Human in terminal sees a pretty table
td ls

# Agent piping output gets JSON
td ls | jq '.data[].content'
```

Force a specific format:

```bash
td ls --json     # JSON even in TTY
td ls --plain    # Tab-separated, no color — for cut/awk
```

### Capability manifest

```bash
td schema
```

Returns a full JSON manifest of all commands, arguments, options, and types. Call once, know everything.

### TTY-aware errors

Errors adapt to context — styled for humans in a terminal, structured for agents when piped:

**Terminal (Rich mode):**
```
Error: Project 'Worx' not found
  Suggestion: Run `td projects` to list available projects. Did you mean 'Work'?
```

**Piped / JSON mode:**
```json
{
  "ok": false,
  "error": {
    "code": "PROJECT_NOT_FOUND",
    "message": "Project 'Worx' not found",
    "suggestion": "Run 'td projects' to list available projects. Did you mean 'Work'?"
  }
}
```

### Idempotent task creation

```bash
td add "Deploy v2.1" -p Releases --idempotent
```

Returns the existing task if identical content already exists. The JSON response includes `"created": false` so agents know no duplicate was made.

## Architecture

```
src/td/
  core/       # Pure business logic — no CLI dependency
    tasks.py, projects.py, labels.py, sections.py, config.py, client.py
  cli/        # Thin Click frontend
    tasks.py, projects.py, labels.py, sections.py, output.py, errors.py
  schema.py   # Click command tree → JSON capability manifest
```

The core is a library. The CLI is one frontend. An MCP server ([planned](https://github.com/craigmccaskill/todoist-cli/issues/27)) will be another — same logic, different protocol.

## Commands

| Command | Description |
|---------|-------------|
| `td add` | Create a task (with project, priority, due date, labels) |
| `td quick` | Natural language task creation |
| `td capture` | Quick-capture to inbox — no parsing, no flags |
| `td ls` | List tasks (defaults to today + overdue, sortable) |
| `td today` | Morning dashboard: overdue + due today |
| `td next` | Show your highest priority task |
| `td inbox` | Show unprocessed inbox tasks |
| `td focus` | Single-project deep work view |
| `td log` | Completed tasks today or this week |
| `td show` | View full task details |
| `td search` | Full-text search across all tasks |
| `td done` | Complete a task (row number, content match, or ID) |
| `td undo` | Reopen a completed task |
| `td edit` | Update a task (same flexible ref) |
| `td move` | Move a task to a different project |
| `td delete` | Delete a task (same flexible ref) |
| `td comment` | Add a comment to a task |
| `td comments` | List comments on a task |
| `td projects` | List projects |
| `td project-add` | Create a new project |
| `td sections` | List sections in a project |
| `td section-add` | Create a new section in a project |
| `td labels` | List labels |
| `td label-add` | Create a new label |
| `td review` | Interactive inbox review TUI (requires `[interactive]`) |
| `td rate-limit` | Show API rate limit status |
| `td schema` | Output capability manifest (JSON) |
| `td init` | Set up authentication (config file or env var) |
| `td completions` | Generate shell completions (bash/zsh/fish) |

See [docs/examples.md](docs/examples.md) for full output examples of every command.

## Configuration

Config lives at `~/.config/td/config.toml` (respects `XDG_CONFIG_HOME`).

```toml
[auth]
api_token = "your-todoist-api-token"
```

Or set `TD_API_TOKEN` as an environment variable (preferred for agents and CI).

## Why td?

Existing options are broken:

- **sachaos/todoist** (~1.4k stars) — semi-abandoned, uses the deprecated Sync API
- **MCP integrations** — auth flakiness, excessive token usage for simple operations
- **Every other CLI** — unstructured output, no introspection, agents can't self-discover capabilities

td closes the gap: a maintained, fast CLI where AI discoverability is a design constraint, not an afterthought.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and guidelines.

## License

[MIT](LICENSE)
