# AI & Agent Integration

td is built for AI agents as a first-class use case — and a lightweight alternative to MCP for Todoist integration.

## Why td for Agents?

MCP servers for Todoist exist, but they suffer from auth flakiness, excessive token consumption, and opaque error handling. td gives agents the same capabilities through a simpler interface:

- **Structured JSON over stdout/stderr** — no protocol overhead
- **Self-describing schema** — one call to `td schema` and the agent knows everything
- **Idempotent operations** — prevents the #1 agent failure mode (duplicate creation)
- **No persistent connection** — stateless CLI calls, no server to maintain

## Quick Start for Agents

```bash
# Set token (no interactive setup needed)
export TD_API_TOKEN="your-token"

# Discover all capabilities
td schema | jq '.commands | keys'

# All output is JSON when piped
td ls | jq '.data[].content'
```

## Topics

- [Structured Output](output.md) — automatic JSON, three output modes
- [Error Handling](errors.md) — TTY-aware errors with codes and suggestions
- [Idempotency](idempotency.md) — preventing duplicate task creation
