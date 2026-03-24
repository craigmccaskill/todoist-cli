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

- `td add <content>` — create task (`-p` project, `--priority` 1-4, `-d` due, `-l` label, `--idempotent`). Reads from stdin if no args
- `td quick <text>` — natural language task creation. Reads from stdin if no args
- `td capture <text>` — quick-capture to inbox, no parsing or flags
- `td ls` — list tasks (defaults to today + overdue). `--all`, `-p`, `-l`, `-f`, `--sort`, `--ids`
- `td today` — overdue + due today, sorted by priority
- `td next` — single highest priority task. `--project` to scope
- `td inbox` — unprocessed inbox tasks
- `td focus <project>` — single-project view, sorted by priority
- `td log` — completed tasks today. `--week` for this week
- `td done <ref>` — complete task (accepts row number from last `td ls` or task ID)
- `td undo <ref>` — reopen a completed task
- `td edit <ref>` — update task fields
- `td delete <ref> --yes` — delete task (use `--yes` to skip confirmation)
- `td projects` — list all projects
- `td project-add <name>` — create a project (`--parent`, `--favorite`)
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
