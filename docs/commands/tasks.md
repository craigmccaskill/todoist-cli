# Task Commands

## td add

Create a new task with optional project, priority, due date, labels, and section.

```bash
td add "Review PR for auth module" -p Work --priority 1 -d tomorrow -l code-review
td add "Design review" -p Work -s "In Progress"
echo "Task from stdin" | td add
```

**Options:**

| Flag | Description |
|------|-------------|
| `-p`, `--project` | Project name or ID (tab-completable) |
| `--priority` | 1=urgent, 2=high, 3=medium, 4=low |
| `-d`, `--due` | Due date (natural language: "tomorrow", "next friday") |
| `-l`, `--label` | Label name, repeatable (tab-completable) |
| `-s`, `--section` | Section name, requires `--project` (tab-completable) |
| `--desc` | Task description |
| `--idempotent` | Skip if identical task already exists |

## td quick

Natural language task creation powered by Todoist's parsing engine.

```bash
td quick "Buy milk tomorrow p2 #Errands"
echo "Deploy hotfix" | td quick
```

## td capture

Quick-capture to inbox with zero friction. No parsing, no flags.

```bash
td capture call dentist about appointment
```

## td done

Complete a task. Confirms on fuzzy match in TTY mode.

```bash
td done 1              # row number
td done buy milk       # fuzzy match (confirms)
td done 8bx9a0c2      # exact ID
td done buy milk -y    # skip confirmation
```

## td undo

Reopen a completed task.

```bash
td undo 8bx9a0c2
```

## td edit

Update task fields. With no flags, shows current values.

```bash
td edit 1 --due friday --priority 2
td edit buy milk --content "Buy whole milk"
td edit 1                  # show current values
```

## td move

Move a task to a different project.

```bash
td move 1 -p Personal
td move buy milk -p Work
```

## td delete

Delete a task. Requires confirmation unless `--yes` is passed.

```bash
td delete 1 -y
td delete buy milk --yes
```

## td show

View full task details including description, project, and all metadata.

```bash
td show 1
td show buy milk
```

## td search

Full-text search across all tasks. Results sorted by relevance.

```bash
td search deploy
td search "blog post" -p Work
```

## td comment

Add a comment to a task.

```bash
td comment 1 "Picked up 2%, not whole"
```

## td comments

List all comments on a task.

```bash
td comments 1
```
