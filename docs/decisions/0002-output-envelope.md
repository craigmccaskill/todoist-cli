# ADR-0002: JSON Output Envelope

## Status

Accepted

## Context

`td` emits output in three modes: Rich (tables for humans), Plain
(flat text for grep and pipes), and JSON (for agents and scripts).
The first two are for reading. JSON is for programmatic consumers
that need to detect success, errors, and result types without
string-matching.

Two shapes were plausible:

1. **Raw data.** Emit the command's result directly. Pros: least
   verbose for simple scripts. Cons: no way to distinguish success
   from failure without inspecting exit code, no way to tag the
   result type, no uniform error shape.
2. **Envelope.** Wrap every result in a consistent outer structure
   with success/error, type, and payload. Pros: a single parser
   handles every command. Cons: one level of nesting on every
   response.

For AI agents consuming `td` output, an envelope wins. The agent can
branch on `ok` before anything else, and can rely on `type` to pick a
parser for the `data` payload. Without the envelope, every command
would need its own out-of-band convention for success detection.

## Decision

All JSON output uses this envelope:

**Success:**

```json
{"ok": true, "type": "<result_type>", "data": <payload>}
```

**Error:**

```json
{"ok": false, "error": {"code": "<code>", "message": "...", "suggestion": "..."}}
```

Errors go to stderr with non-zero exit code. Success goes to stdout
with exit code 0.

- `type` is a stable string identifying the shape of `data` (e.g.
  `"task_list"`, `"task"`, `"project"`).
- `data` is whatever the command returns for that type.
- Error `code` is a stable machine-readable identifier (e.g.
  `"not_found"`, `"ambiguous_match"`, `"api_error"`).
- `message` is the human-readable description.
- `suggestion` is specific guidance on what to do next.

`cli/output.py`'s `OutputFormatter` is the single source of envelope
construction. No command emits JSON directly.

## Consequences

**Positive.** A single parser in an agent or script handles every
command. Success/failure detection is reliable without exit-code
inspection. Error codes are stable and switchable. Type tags allow
result-shape dispatch without per-command string-matching hacks.

**Negative.** One level of nesting on every response, which is
verbose for scripts that know exactly what they're calling. The
envelope is a contract: any change to field names or nesting is a
breaking change and requires a superseding ADR.

**Discipline.** Adding a new result type means adding a new `type`
string, not extending an existing one. The schema emitted by
`td schema` (ADR-0006) must list every `type` string the CLI can
produce, so agents can discover them.
