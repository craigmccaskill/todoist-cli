# Commands Reference

td's commands are organized by function. Use `td <command> --help` for
detailed options, or `td schema` for the full machine-readable manifest.

## Task Management

| Command | Description |
|---------|-------------|
| [`td add`](tasks.md#td-add) | Create a task with project, priority, due date, labels, section |
| [`td quick`](tasks.md#td-quick) | Natural language task creation |
| [`td capture`](tasks.md#td-capture) | Quick-capture to inbox |
| [`td done`](tasks.md#td-done) | Complete a task |
| [`td undo`](tasks.md#td-undo) | Reopen a completed task |
| [`td edit`](tasks.md#td-edit) | Update task fields |
| [`td move`](tasks.md#td-move) | Move a task to a different project |
| [`td delete`](tasks.md#td-delete) | Delete a task |
| [`td show`](tasks.md#td-show) | View full task details |
| [`td search`](tasks.md#td-search) | Full-text search across all tasks |

## Workflow

| Command | Description |
|---------|-------------|
| [`td ls`](workflow.md#td-ls) | List tasks (defaults to today + overdue) |
| [`td today`](workflow.md#td-today) | Morning dashboard |
| [`td next`](workflow.md#td-next) | Highest priority task |
| [`td inbox`](workflow.md#td-inbox) | Unprocessed inbox tasks |
| [`td focus`](workflow.md#td-focus) | Single-project deep work view |
| [`td log`](workflow.md#td-log) | Completed tasks |
| [`td review`](workflow.md#td-review) | Interactive inbox processing TUI |

## Organization

Entity groups for projects, sections, labels, and comments. Each group
exposes `list`, `add`, `edit`, `delete` subcommands (plus `archive` /
`unarchive` on `project`). The flat plural forms (`td projects`, etc.)
are permanent shortcuts for the list case. See
[ADR-0009](../decisions/0009-crud-verb-grammar.md) for the grammar
decision.

| Command | Description |
|---------|-------------|
| [`td projects`](organization.md#td-projects-td-project-list) | List projects |
| [`td project add`](organization.md#td-project-add) | Create a project |
| [`td project edit`](organization.md#td-project-edit) | Rename or recolor a project |
| [`td project delete`](organization.md#td-project-delete) | Delete a project |
| [`td project archive`](organization.md#td-project-archive-unarchive) | Archive a project |
| [`td project unarchive`](organization.md#td-project-archive-unarchive) | Unarchive a project |
| [`td sections`](organization.md#td-sections-td-section-list) | List sections |
| [`td section add`](organization.md#td-section-add) | Create a section in a project |
| [`td section edit`](organization.md#td-section-edit) | Rename a section |
| [`td section delete`](organization.md#td-section-delete) | Delete a section |
| [`td labels`](organization.md#td-labels-td-label-list) | List labels |
| [`td label add`](organization.md#td-label-add) | Create a label |
| [`td label edit`](organization.md#td-label-edit) | Rename or recolor a label |
| [`td label delete`](organization.md#td-label-delete) | Delete a label |
| [`td comments`](organization.md#td-comments-td-comment-list) | List comments on a task |
| [`td comment`](organization.md#td-comment-add) | Add a comment (flat shortcut) |
| [`td comment add`](organization.md#td-comment-add) | Add a comment |
| [`td comment edit`](organization.md#td-comment-edit) | Update a comment |
| [`td comment delete`](organization.md#td-comment-delete) | Delete a comment |

## Utilities

| Command | Description |
|---------|-------------|
| [`td schema`](utilities.md#td-schema) | Capability manifest (JSON) |
| [`td rate-limit`](utilities.md#td-rate-limit) | API rate limit status |
| [`td init`](utilities.md#td-init) | Authentication setup |
| [`td completions`](utilities.md#td-completions) | Shell completion scripts |

## Task References

All task commands accept flexible references:

- **Row number** — `td done 1` (from the last `td ls` output)
- **Content match** — `td done buy milk` (fuzzy match)
- **Task ID** — `td done 8bx9a0c2` (exact ID)
