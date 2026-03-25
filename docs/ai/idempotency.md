# Idempotent Operations

## The Problem

AI agents retry failed operations. Without idempotency, a retry creates a duplicate task. This is the #1 failure mode for agent-managed task lists.

## The Solution

```bash
td add "Deploy v2.1" -p Releases --idempotent
```

If a task with identical content already exists in the target project, td returns the existing task instead of creating a duplicate.

## Response

The JSON response includes a `created` field:

**New task created:**
```json
{
  "ok": true,
  "type": "task_created",
  "data": {
    "id": "8bx9a0c2",
    "content": "Deploy v2.1",
    "created": true
  }
}
```

**Existing task returned:**
```json
{
  "ok": true,
  "type": "task_created",
  "data": {
    "id": "8bx9a0c2",
    "content": "Deploy v2.1",
    "created": false
  }
}
```

Agents check `data.created` to know whether a new task was made.
