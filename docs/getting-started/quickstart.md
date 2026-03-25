# Quick Start

## Authentication

Set up your API token:

```bash
td init
```

Or set the environment variable directly:

```bash
export TD_API_TOKEN="your-token-here"
```

Get your token from [Todoist Developer Settings](https://app.todoist.com/app/settings/integrations/developer).

## Your First Commands

```bash
# See what's due today
td today

# Add a task
td add "Review PR for auth module" -p Work --priority 1 -d tomorrow

# Quick natural language add
td quick "Buy milk tomorrow p2 #Errands"

# Quick capture to inbox
td capture call dentist about appointment

# Complete a task (fuzzy match)
td done buy milk

# Search across all tasks
td search deploy

# View full task details
td show 1
```

## Default Command

Running `td` with no subcommand shows your today view:

```bash
td          # same as td today
```

Configure the default in `~/.config/td/config.toml`:

```toml
[settings]
default_command = "today"  # or "ls", "inbox", "next"
```
