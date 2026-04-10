# A day with td

This is what using td looks like — not a command reference, but a workday.

## Morning

You sit down with coffee. What's waiting?

```bash
$ td
```

Overdue items from yesterday, today's deadlines, that auth bug you forgot to
close. All in one view with priority bars and due dates.

What about tomorrow?

```bash
$ td tomorrow
```

Heavy day ahead. And the rest of the week:

```bash
$ td upcoming
```

Or just the next few days:

```bash
$ td upcoming 3
```

Too much in the inbox?

```bash
$ td inbox
```

Process it: knock out the quick ones, move others to projects.

```bash
$ td done 3
$ td done 1 5
```

## Capture

Interrupts happen all day. Don't switch contexts — just capture and move on:

```bash
$ td add investigate memory leak in staging
$ td add review Q3 roadmap draft by Friday p1
$ td add buy birthday present for mom this weekend
$ td add schedule 1:1 with Alex tomorrow
```

No flags, no quoting. Todoist's NLP handles dates and priorities. When you
need precision for a specific project:

```bash
$ td add "Deploy v2.1" --project Releases --priority 1 --due 2026-04-15
```

## Focus

Deep work time. Zoom into one project:

```bash
$ td focus Work
```

Just the Work tasks, sorted by priority. Everything else disappears.

Need to find something you half-remember?

```bash
$ td search deploy
```

What's overdue across all projects?

```bash
$ td overdue
```

Just overdue in Work?

```bash
$ td overdue Work
```

## Complete

Knock things out by row number, name, or however you remember them:

```bash
$ td done 2
$ td done buy milk
$ td done 1 3 5
```

Made a mistake?

```bash
$ td undo 2
```

## End of day

What did I actually get done?

```bash
$ td completed
```

Everything checked off today. Or look back further:

```bash
$ td completed 7d
$ td completed Work 2w
```

## Check your setup

New install? Something not working?

```bash
$ td doctor
```

One command to verify Python, config, auth, connectivity, and shell completions.

## For scripts and agents

When td is piped, it outputs structured JSON automatically:

```bash
$ td ls --json | jq '.data[] | select(.priority == 4) | .content'
```

Agents can discover all commands and install a skill file:

```bash
$ td schema              # full command manifest as JSON
$ td skill install       # install command reference for Claude Code
```

Every error includes a code and suggestion:

```json
{
  "ok": false,
  "error": {
    "code": "TASK_NOT_FOUND",
    "message": "Task 'xyz' not found.",
    "suggestion": "Use a row number from `td ls`, a task name, or a task ID."
  }
}
```

For the full command reference, run `td --help` or see the
[documentation site](https://craigmccaskill.github.io/todoist-cli).
