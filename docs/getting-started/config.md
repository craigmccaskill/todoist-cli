# Configuration

Config lives at `~/.config/td/config.toml` (respects `XDG_CONFIG_HOME`).

## Config File

```toml
[auth]
api_token = "your-todoist-api-token"

[settings]
default_command = "today"    # command to run when td is called with no args
default_format = "rich"      # "rich", "plain", or "json"
default_sort = "priority"    # "priority", "due", "project", "created"
color = true                 # set false to disable colors
```

## Environment Variables

Environment variables override config file values:

| Variable | Description | Example |
|----------|-------------|---------|
| `TD_API_TOKEN` | API token (preferred for agents/CI) | `export TD_API_TOKEN="abc..."` |
| `TD_FORMAT` | Default output format | `export TD_FORMAT="json"` |
| `TD_SORT` | Default sort order | `export TD_SORT="due"` |
| `TD_DEFAULT_CMD` | Default command | `export TD_DEFAULT_CMD="inbox"` |
| `TD_DEBUG` | Enable debug logging | `export TD_DEBUG=1` |
| `NO_COLOR` | Disable all colors | `export NO_COLOR=1` |

## Resolution Order

For each setting, the most specific source wins:

1. CLI flags (`--json`, `--plain`, `--sort`)
2. Environment variables (`TD_FORMAT`, `TD_SORT`)
3. Config file (`~/.config/td/config.toml`)
4. Built-in defaults
