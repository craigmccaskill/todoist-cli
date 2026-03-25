# Utility Commands

## td schema

Output a full capability manifest as JSON. Agents call this once to learn every command, argument, option, and type.

```bash
td schema
td schema | jq '.commands | keys'
```

## td rate-limit

Show current API rate limit status from cached response headers. No API call required.

```bash
td rate-limit
```

Todoist allows 450 requests per 15 minutes. td monitors usage automatically and warns to stderr when approaching the limit.

## td init

Interactive authentication setup. Guides you through setting up your API token via config file or environment variable.

```bash
td init
```

## td completions

Generate shell completion scripts.

```bash
td completions bash
td completions zsh
td completions fish
```

See [Installation](../getting-started/install.md) for setup instructions.
