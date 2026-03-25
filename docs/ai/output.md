# Structured Output

## Automatic JSON

When stdout is not a TTY (piped or called by an agent), td outputs structured JSON automatically:

```bash
# Human in terminal sees a pretty table
td ls

# Agent piping output gets JSON
td ls | jq '.data[].content'
```

## Three Output Modes

Force a specific format with flags:

```bash
td ls --json     # JSON even in TTY
td ls --plain    # Tab-separated, no color — for cut/awk
```

Or set a default:

```bash
export TD_FORMAT="json"
```

## Response Format

All JSON responses follow the same envelope:

```json
{
  "ok": true,
  "type": "task_list",
  "data": [...]
}
```

The `type` field identifies the response kind: `task_list`, `task`, `success`, `project_list`, etc.
