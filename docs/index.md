# td — AI-Native Todoist CLI

A modern Todoist CLI built for both humans and AI agents. 29 commands, TTY-aware output, interactive TUI.

## Why td?

Existing options are broken:

- **sachaos/todoist** (~1.4k stars) — semi-abandoned, uses the deprecated Sync API
- **MCP integrations** — auth flakiness, excessive token usage for simple operations
- **Every other CLI** — unstructured output, no introspection, agents can't self-discover capabilities

td closes the gap: a maintained, fast CLI where AI discoverability is a design constraint, not an afterthought.

## Key Features

- **TTY-aware everything** — pretty Rich tables for humans, structured JSON when piped. No flags needed.
- **Interactive TUI** — `td review` opens an inbox-processing interface with keyboard navigation. Commands launch task pickers when called with no args.
- **Fuzzy task matching** — `td done buy milk` finds and completes the right task. Confirms before acting on ambiguous matches.
- **AI-native** — capability manifest via `td schema`, structured errors with codes, idempotent operations.
- **Rate limit awareness** — monitors API usage, warns before you hit the limit.

## Quick Links

- [Installation](getting-started/install.md)
- [Quick Start](getting-started/quickstart.md)
- [Commands Reference](commands/index.md)
- [AI/Agent Integration](ai/index.md)
- [GitHub Repository](https://github.com/craigmccaskill/todoist-cli)
- [Roadmap](https://github.com/users/craigmccaskill/projects/1)
