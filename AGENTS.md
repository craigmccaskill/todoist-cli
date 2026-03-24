# AGENTS.md — Instructions for AI agents using td

## What is td?

AI-native CLI for Todoist. Designed for both humans and LLM agents.

## Quick Start

1. Set `TD_API_TOKEN` environment variable (or run `td init` interactively)
2. Run `td schema` to get a full JSON capability manifest
3. All commands support `--json` for structured output
4. Errors are JSON on stderr with codes and suggestions

## Authentication

Set `TD_API_TOKEN` env var (preferred for agents), or run `td init` interactively.

## Commands

- `td add <content>` — create task (`-p` project, `--priority` 1-4, `-d` due date, `-l` label, `--idempotent`)
- `td quick <text>` — natural language task creation (e.g., "Buy milk tomorrow p1 #Errands")
- `td ls` — list tasks (`-p` project, `-l` label, `-f` filter query)
- `td inbox` — show unprocessed inbox tasks
- `td done <id>` — complete task
- `td undo <id>` — reopen a completed task
- `td edit <id>` — update task fields
- `td delete <id> --yes` — delete task (use `--yes` to skip confirmation)
- `td projects` — list all projects
- `td sections -p <project>` — list sections in a project
- `td labels` — list all labels
- `td schema` — full capability manifest as JSON

## Piping Behavior

When stdout is not a TTY, all output is JSON automatically. No flags needed.
Errors always go to stderr as structured JSON.

## Idempotency

Use `td add --idempotent <content>` to skip creation if a matching task already exists.
JSON output includes `"created": true` or `"created": false`.

## Error Codes

| Code | Meaning |
|------|---------|
| `AUTH_MISSING` | No API token configured |
| `AUTH_INVALID` | API token is invalid |
| `TASK_NOT_FOUND` | Task ID does not exist |
| `PROJECT_NOT_FOUND` | Project name/ID does not exist |
| `VALIDATION_ERROR` | Invalid input parameters |
| `API_ERROR` | Todoist API returned an error |
| `API_RATE_LIMIT` | Rate limit exceeded (retry after delay) |
| `DUPLICATE_TASK` | Task already exists (with `--idempotent`) |

## Error Response Format

```json
{
  "ok": false,
  "error": {
    "code": "PROJECT_NOT_FOUND",
    "message": "Project 'Worx' not found",
    "suggestion": "Run 'td projects' to list available projects. Did you mean 'Work'?",
    "details": {}
  }
}
```

## Success Response Format

```json
{
  "ok": true,
  "type": "task_list",
  "data": [...]
}
```

## Development

```bash
pip install -e ".[dev]"
pytest
ruff check .
mypy td/
```

## Architecture

- `td/core/` — pure business logic, no CLI dependency
- `td/cli/` — Click commands and output formatting
- `td/schema.py` — capability manifest generator
