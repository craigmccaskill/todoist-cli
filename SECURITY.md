# Security Policy

## Supported Versions

| Version | Supported |
|---------|-----------|
| 0.1.x   | Yes       |

## Reporting a Vulnerability

If you discover a security vulnerability in td, please report it responsibly.

**Do not open a public GitHub issue.**

Instead, use [GitHub's private vulnerability reporting](https://github.com/craigmccaskill/todoist-cli/security/advisories/new) to submit your report. You'll receive a response within 7 days.

## What Qualifies

Security issues for this project include:

- **Token exposure** — API tokens leaked in logs, output, or error messages
- **Config file permissions** — insecure default permissions on `~/.config/td/config.toml`
- **Command injection** — user input passed unsafely to shell commands
- **Dependency vulnerabilities** — known CVEs in direct dependencies

## What Doesn't Qualify

- Feature requests or general bugs (use [GitHub Issues](https://github.com/craigmccaskill/todoist-cli/issues))
- Todoist API vulnerabilities (report to [Doist](https://todoist.com/security))
