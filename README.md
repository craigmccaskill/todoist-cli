# td — AI-Native Todoist CLI

[![CI](https://github.com/craigmccaskill/todoist-cli/actions/workflows/ci.yml/badge.svg)](https://github.com/craigmccaskill/todoist-cli/actions/workflows/ci.yml)
[![PyPI version](https://img.shields.io/pypi/v/todoist-cli.svg)](https://pypi.org/project/todoist-cli/)
[![Python versions](https://img.shields.io/pypi/pyversions/todoist-cli.svg)](https://pypi.org/project/todoist-cli/)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![codecov](https://codecov.io/gh/craigmccaskill/todoist-cli/branch/main/graph/badge.svg)](https://codecov.io/gh/craigmccaskill/todoist-cli)

A modern Todoist CLI built on REST API v2, designed for both humans and AI agents.

<!-- TODO: Add terminal demo GIF here -->
<!-- ![td demo](docs/demo.gif) -->

## Why td?

- **sachaos/todoist** (~1.4k stars) is semi-abandoned and uses the deprecated Sync API
- **MCP integrations** are plagued by auth flakiness and burn excessive tokens on simple operations
- **No existing CLI is AI-discoverable** — agents can't introspect capabilities, errors are unstructured, output assumes a human reader

**td** is the first CLI designed with AI discoverability as a first-class concern.

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

When stdout is not a TTY (i.e., piped or called by an agent), td outputs structured JSON automatically. No flags needed.

```bash
# Human in terminal sees a pretty table
td ls

# Agent piping output gets JSON
td ls | jq '.data[].content'
```

You can also force output format:

```bash
td ls --json     # Force JSON even in TTY
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

Returns the existing task if identical content already exists in the project. Prevents the most common agent failure mode.

## Configuration

Config lives at `~/.config/td/config.toml` (respects `XDG_CONFIG_HOME`).

```toml
[auth]
api_token = "your-todoist-api-token"
```

You can also set `TD_API_TOKEN` as an environment variable (preferred for agents and CI).

## Shell Completions

```bash
# Generate completion script
td completions zsh   # or bash, fish

# Add to your shell profile
eval "$(td completions zsh)"
```

## Commands

| Command | Description |
|---------|-------------|
| `td add` | Create a task |
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
| `td completions` | Generate shell completions |

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and guidelines.

## License

[MIT](LICENSE)
