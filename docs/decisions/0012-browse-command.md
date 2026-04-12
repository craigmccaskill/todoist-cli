# ADR-0012: Browse command for opening tasks and projects in the browser

## Status

Accepted

## Context

Issue #220 requests a command to jump from the CLI to the Todoist web app
for a specific task or project. The Todoist API client already exposes
`Task.url` and `Project.url` as computed properties, so no URL
construction is needed.

The design questions are: command name, scope (which entities), behavior
in non-browser contexts (piped output, SSH, `--json`), and whether to
auto-detect entity type or require a flag.

## Alternatives considered

**Name:** `browse` (chosen), `open` (conflicts with shell builtin on
macOS), `web` (ambiguous). `browse` matches `gh browse`, which is the
closest CLI precedent.

**Scope:** Tasks and projects only. Sections, labels, and comments do
not have stable web URLs in the Todoist app. Sections and labels are
addressable only as query parameters, not direct links.

**Flag-only entity selection** (`-p` required for projects): rejects
auto-detection in favor of explicit typing. Violates ADR-0001's core
principle: "The common case should be flag-free. Flags are for
disambiguation." The user typing `td browse Work` means "open the
thing called Work," not "tell me which entity type you want first."

**Subcommand on entity groups** (`td project browse Work`): `browse` is
not a CRUD verb. It crosses entity types and fits the pattern of
top-level utility commands like `show` and `search`. Adding it as a
verb on every entity group would double the surface for no clarity gain.

## Decision

Add a top-level `td browse` command as a flat utility command.

- **Auto-detection:** resolve the ref by trying task ref resolution
  first (ADR-0004 chain: row number, content match, task ID), then
  project name match. If both match, show an interactive picker in TTY
  mode (ADR-0001 S3: ambiguous input triggers a picker, not a failure).
  In non-TTY mode, prefer the task match and print a hint to stderr.
- **`-p`/`--project` flag:** disambiguation shortcut that skips task
  resolution and goes straight to `resolve_project()`. Exists for the
  edge case where a task and project share a name, not as the default
  path.
- **No arguments:** open the Todoist inbox
  (`https://app.todoist.com/app/inbox`), matching `gh browse` opening
  the repo root.
- **`--url-only`/`-u` flag:** print the URL to stdout instead of
  launching the browser. Useful for piping, SSH sessions, and agents.
- **`--json` mode:** emit `{"ok": true, "type": "url", "data": {"url":
  "...", "entity": "task|project"}}` without launching a browser.
- **stderr confirmation:** when launching the browser, print the URL to
  stderr as a one-line confirmation (same pattern as `gh browse`).

Browser-opening logic (`click.launch`) lives in `cli/`, not `core/`,
per ADR-0005. No new `core/` module is needed.

## Consequences

**Positive:** One-step jump from CLI to web app. Agents can extract
task/project URLs via `--json` without screen-scraping. Follows
established precedent (`gh browse`).

**Negative:** Adds one more top-level command to the already-growing
`--help` surface. The `--url-only` flag name is slightly unusual
(`gh browse` uses `-n`/`--no-browser`); we chose `--url-only` because
it describes what happens, not what doesn't.

## References

- #220
- ADR-0001 (design principle)
- ADR-0004 (task ref resolution)
- ADR-0005 (core/cli boundary)
- `gh browse` as CLI precedent
