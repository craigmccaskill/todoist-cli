# Commands Reference

td has 29 commands organized by function.

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
| [`td comment`](tasks.md#td-comment) | Add a comment to a task |
| [`td comments`](tasks.md#td-comments) | List comments on a task |

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

| Command | Description |
|---------|-------------|
| [`td projects`](organization.md#td-projects) | List projects |
| [`td project-add`](organization.md#td-project-add) | Create a project |
| [`td sections`](organization.md#td-sections) | List sections |
| [`td section-add`](organization.md#td-section-add) | Create a section |
| [`td labels`](organization.md#td-labels) | List labels |
| [`td label-add`](organization.md#td-label-add) | Create a label |

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
