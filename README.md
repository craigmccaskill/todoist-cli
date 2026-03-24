# td — AI-Native Todoist CLI

[![CI](https://github.com/craigmccaskill/todoist-cli/actions/workflows/ci.yml/badge.svg)](https://github.com/craigmccaskill/todoist-cli/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

> A modern Todoist CLI built on REST API v2, designed for both humans and AI agents.

**Status:** Alpha — feature-complete for core task management. [See the roadmap.](https://github.com/users/craigmccaskill/projects/1)

<!-- TODO: Replace with terminal recording -->
<!-- ![td demo](docs/demo.gif) -->

## Features

- **TTY-aware output** — pretty tables for humans, structured JSON when piped. No flags needed.
- **Capability manifest** — `td schema` dumps every command, argument, and option as JSON. An agent calls it once and knows everything.
- **Structured errors** — machine-readable error codes and actionable suggestions on stderr.
- **Idempotent operations** — `--idempotent` flag prevents duplicate task creation, solving the #1 agent failure mode.
- **Natural language input** — `td quick "Buy milk tomorrow p1 #Errands"` parsed by Todoist's engine.
- **Three output modes** — Rich (terminal), JSON (agents/pipes), Plain (cut/awk).
- **Library-first architecture** — CLI and future MCP server are thin frontends over the same tested core.

## Install

```bash
pip install todoist-cli
```

Requires Python 3.10+.

## Quick Start

```bash
# Set up authentication
td init

# Add a task
td add "Review PR for auth module" -p Work --priority 1 -d tomorrow

# Natural language quick add
td quick "Buy milk tomorrow p2 #Errands"

# List tasks
td ls
td ls -p Work
td ls -f "today & #Work"

# View your inbox
td inbox

# Complete a task
td done <task-id>

# Edit a task
td edit <task-id> --due "next monday"

# Delete a task
td delete <task-id>
```

## AI / Agent Usage

td is built for AI agents as a first-class use case.

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

### Structured errors

Errors go to stderr as structured JSON with codes and actionable suggestions:

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
td/
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
| `td ls` | List and filter tasks |
| `td inbox` | Show unprocessed inbox tasks |
| `td done` | Complete a task |
| `td edit` | Update a task |
| `td delete` | Delete a task |
| `td projects` | List projects |
| `td sections` | List sections in a project |
| `td labels` | List labels |
| `td schema` | Output capability manifest (JSON) |
| `td init` | Set up authentication |
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
