# Error Handling

## TTY-Aware Errors

Errors adapt to context automatically:

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
    "suggestion": "Run 'td projects' to list available projects. Did you mean 'Work'?",
    "details": {}
  }
}
```

Errors always go to **stderr**, keeping stdout clean for data.

## Error Codes

| Code | Meaning |
|------|---------|
| `AUTH_MISSING` | No API token configured |
| `AUTH_INVALID` | API token is invalid |
| `TASK_NOT_FOUND` | Task ID does not exist |
| `PROJECT_NOT_FOUND` | Project name/ID does not exist |
| `SECTION_NOT_FOUND` | Section name/ID does not exist |
| `LABEL_NOT_FOUND` | Label name/ID does not exist |
| `VALIDATION_ERROR` | Invalid input parameters |
| `API_ERROR` | Todoist API returned an error |
| `API_RATE_LIMIT` | Rate limit exceeded |
| `DUPLICATE_TASK` | Task already exists (with `--idempotent`) |

## Handling Errors in Code

```python
import subprocess, json

result = subprocess.run(["td", "--json", "done", "bad-id"], capture_output=True, text=True)
if result.returncode != 0:
    error = json.loads(result.stderr)
    code = error["error"]["code"]
    suggestion = error["error"]["suggestion"]
```
