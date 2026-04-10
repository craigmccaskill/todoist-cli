# todoist-cli

[![CI](https://github.com/craigmccaskill/todoist-cli/actions/workflows/ci.yml/badge.svg)](https://github.com/craigmccaskill/todoist-cli/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

Manage your Todoist from the terminal. Pretty tables when you're at the
keyboard, structured JSON when your scripts and AI agents are driving.

![td demo](docs/demo/demo.gif)

## Install

```bash
pip install git+https://github.com/craigmccaskill/todoist-cli.git
td init
td completions install
```

Requires Python 3.10+.

## Your morning

```bash
td                        # what needs your attention (today + overdue)
td tomorrow               # plan ahead
td upcoming               # next 7 days
td overdue                # just the overdue pile
```

## Capture without breaking flow

```bash
td add call dentist tomorrow
td add review Q3 roadmap draft Friday p1
td add buy birthday present for mom this weekend
```

No flags needed. Todoist's NLP parses dates, priorities, and projects from
natural language. When you need precision:

```bash
td add "Deploy v2.1" --project Releases --priority 1 --due 2026-04-15
```

## Get things done

Row numbers from `td` work everywhere. No IDs to copy.

```bash
td done 2                 # complete task #2
td done 2 4 5             # batch complete
td done buy milk          # fuzzy match by name
```

Made a mistake? `td undo 2`.

## See one project

```bash
td focus Work             # just Work's tasks
td overdue Work           # overdue in Work only
td completed Work 7d      # what you finished this week
```

## When things go wrong

td tells you what happened and what to try:

```
Error: Task "ljasdf" not found.
  Suggestion: Use a row number from `td ls`, a task name, or a task ID.
```

Ambiguous match? td asks you to pick. No arguments? td launches a picker.

## Check your setup

```bash
td doctor
```

One command to verify Python, config, auth, and connectivity.

## Make it yours

```toml
# ~/.config/td/config.toml
[settings]
default_command = "today"     # what `td` with no args runs
default_sort = "due"          # priority, due, project, created
cache_ttl_results = 300       # how long row numbers stay valid
```

## For scripts and AI agents

Output adapts automatically. Pipe td and you get JSON:

```bash
td ls | jq '.data[].content'
```

Agents can self-discover everything:

```bash
td schema          # full command manifest as JSON
td skill install   # install command reference for Claude Code
```

Idempotent operations, structured error codes, `--json` and `--plain` flags
on every command. See the [examples guide](docs/examples.md) for more.

## Full command list

Run `td --help` or see the [documentation site](https://craigmccaskill.github.io/todoist-cli).

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup and guidelines.

## License

[MIT](LICENSE)
