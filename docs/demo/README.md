# Demo Recording

Setup instructions and VHS tape file for recording the `td` CLI demo GIF used in the project README.

## Prerequisites

```bash
brew install vhs gifsicle
```

## Demo Data Setup

Create these tasks before recording. All demo data should use project names that don't collide with real tasks.

**Work project:**
```bash
td add "Review Q2 report" -p Work --priority 1 -d today
td add "Update API docs" -p Work --priority 2 -d Monday
td add "Sprint planning agenda" -p Work --priority 3
td add "Sprint demo prep" -p Work --priority 2 -d friday
```

**Personal project:**
```bash
td add "Buy milk and eggs" -p Personal --priority 4 -d today
td add "Call dentist" -p Personal --priority 3
```

**Inbox:**
```bash
td capture "Look into standing desk options"
td capture "Reply to Sarah about dinner"
```

> **Important:** Before recording, reschedule any real tasks due today so only demo tasks appear in `td today`.

## Recording

```bash
vhs demo.tape
gifsicle -O3 demo.gif -o demo.gif
```

The output `demo.gif` is committed to this directory and referenced by the project README.

## Story Arc (~20s)

1. **Morning check-in** — `td today` shows the Rich table
2. **Knock one out** — `td done buy milk` fuzzy matches and confirms
3. **Quick capture** — `td capture ...` minimal-friction inbox capture
4. **Power add** — `td add` with project, priority, due date flags
5. **Search** — `td search sprint` finds tasks by keyword

### Future: Claude integration beat

A beat showing Claude Code adding tasks via `td` is planned but deferred. Challenges to solve:
- Claude explores the CLI before acting — needs a more directive prompt
- Permission prompts appear in the recording — needs pre-allowed tools in project settings
- Model/speed tuning — sonnet recommended, set via `~/.claude/settings.json`

## Cleanup

After recording, remove all demo tasks and restore any rescheduled real tasks.
