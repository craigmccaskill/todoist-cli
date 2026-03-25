"""Configuration commands: init, completions."""

from __future__ import annotations

import os

import click
from todoist_api_python.api import TodoistAPI

from td.core.config import TdConfig, get_config_path, load_config, save_config


@click.command()
def init() -> None:
    """Set up authentication and configuration."""
    existing = load_config()
    config_path = get_config_path()

    if existing.api_token and config_path.exists():
        overwrite = click.confirm(
            f"Config already exists at {config_path}. Overwrite?",
            default=False,
        )
        if not overwrite:
            click.echo("Aborted.")
            return

    click.echo(
        "Get your API token from: https://app.todoist.com/app/settings/integrations/developer"
    )
    click.echo()

    token = click.prompt("API token", hide_input=True)

    # Validate the token
    click.echo("Validating token...")
    try:
        api = TodoistAPI(token)
        projects = list(next(iter(api.get_projects())))
        click.echo(f"Authenticated. Found {len(projects)} project(s).")
    except Exception as e:
        click.echo(f"Error: Could not authenticate — {e}", err=True)
        raise SystemExit(1) from None

    # Ask where to store the token
    click.echo()
    click.echo("How would you like to store your token?")
    click.echo("  1. Config file (recommended for personal machines)")
    click.echo("  2. Environment variable (recommended for CI/agents)")
    choice = click.prompt("Choice", type=click.IntRange(1, 2), default=1)

    if choice == 1:
        config = TdConfig(api_token=token)
        path = save_config(config)
        click.echo()
        click.echo(f"Config saved to {path}")
    else:
        shell = os.environ.get("SHELL", "/bin/bash")
        click.echo()
        if "fish" in shell:
            click.echo("Add to ~/.config/fish/config.fish:")
            click.echo(f'  set -x TD_API_TOKEN "{token}"')
        else:
            click.echo("Add to your shell profile (~/.bashrc, ~/.zshrc):")
            click.echo(f'  export TD_API_TOKEN="{token}"')
        click.echo()
        click.echo("Or for a .env file:")
        click.echo(f"  TD_API_TOKEN={token}")

    click.echo()
    click.echo("Try `td ls` to see your tasks.")


@click.command()
@click.argument("shell", type=click.Choice(["bash", "zsh", "fish"]))
def completions(shell: str) -> None:
    """Generate shell completion script.

    Add the output of this command to your shell profile.
    """
    var = "_TD_COMPLETE"
    if shell == "bash":
        click.echo(f'eval "$({var}=bash_source td)"')
    elif shell == "zsh":
        click.echo(f'eval "$({var}=zsh_source td)"')
    elif shell == "fish":
        click.echo(f"{var}=fish_source td | source")
