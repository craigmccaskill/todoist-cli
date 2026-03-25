# Workflow Commands

## td ls

List tasks. Defaults to today + overdue unless filtered.

```bash
td ls                        # today + overdue
td ls --all                  # everything
td ls -p Work --sort due     # project filter, sorted
td ls -f "today & #Work"    # Todoist filter syntax
td ls --ids                  # output only task IDs (for piping)
```

**Options:**

| Flag | Description |
|------|-------------|
| `-p`, `--project` | Filter by project (tab-completable) |
| `-l`, `--label` | Filter by label (tab-completable) |
| `-f`, `--filter` | Todoist filter query |
| `--all` | Show all tasks (override default filter) |
| `--sort` | Sort by: priority, due, project, created |
| `--reverse` | Reverse sort order |
| `--ids` | Output only task IDs, one per line |

## td today

Morning dashboard — overdue + due today, sorted by priority.

```bash
td today
td today --sort due
```

## td next

Show your single highest priority task.

```bash
td next
td next -p Work    # scope to a project
```

## td inbox

Show unprocessed inbox tasks.

```bash
td inbox
```

## td focus

Single-project deep work view.

```bash
td focus Work
td focus Work --sort due --reverse
```

## td log

Completed tasks — your end-of-day review.

```bash
td log           # completed today
td log --week    # completed this week
```

## td review

Interactive TUI for inbox processing. Requires `todoist-cli[interactive]`.

```bash
td review              # review inbox
td review -p Work      # review a project
td review -f "no date" # review tasks matching a filter
```

**Keyboard shortcuts:**

| Key | Action |
|-----|--------|
| `j` / `↓` | Move cursor down |
| `k` / `↑` | Move cursor up |
| `p` | Set project |
| `d` | Set due date |
| `r` | Set priority |
| `l` | Add label |
| `x` | Mark as done |
| `u` | Undo last action |
| `h` | Toggle shortcut bar |
| `?` | Show help |
| `q` | Quit with summary |
