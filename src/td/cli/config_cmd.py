"""Configuration commands: init, completions."""

from __future__ import annotations

import logging
import os

import click
from rich.console import Console
from todoist_api_python.api import TodoistAPI

from td.core.config import TdConfig, get_config_path, load_config, save_config

_TODOIST_SETTINGS_URL = "https://app.todoist.com/app/settings/integrations/developer"


@click.command()
def init() -> None:
    """Set up authentication and configuration."""
    console = Console(stderr=False)
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

    console.print(
        "Your API token lets td read and manage your Todoist tasks. "
        "The token is stored locally on this machine and is never sent "
        "anywhere except the Todoist API."
    )
    console.print()
    console.print(
        "Get your token here: "
        f"[link={_TODOIST_SETTINGS_URL}]Todoist Settings → "
        f"Integrations → Developer[/link]"
    )
    console.print()

    token = click.prompt("API token", hide_input=True)

    # Validate the token
    click.echo("Validating token...")
    try:
        api = TodoistAPI(token)
        projects = list(next(iter(api.get_projects())))
        click.echo(f"Authenticated. Found {len(projects)} project(s).")
    except Exception as e:
        logging.getLogger(__name__).debug("Token validation failed: %s", e, exc_info=True)
        _handle_auth_error(e)

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
        click.echo("Run this command to set your token (it won't appear in shell history):")
        click.echo()
        if "fish" in shell:
            click.echo("  read -s -P 'Token: ' TD_API_TOKEN && set -x TD_API_TOKEN $TD_API_TOKEN")
        else:
            click.echo("  read -rs TD_API_TOKEN && export TD_API_TOKEN")
        click.echo()
        click.echo("To persist it, add TD_API_TOKEN to your shell profile or .env file.")

    click.echo()
    click.echo("Try `td ls` to see your tasks.")


def _handle_auth_error(e: Exception) -> None:
    """Provide specific guidance based on the type of auth failure."""
    from httpx import ConnectError, HTTPStatusError

    msg: str
    if isinstance(e, HTTPStatusError) and e.response.status_code == 401:
        msg = (
            "Token validation failed. Make sure you copied the full token "
            "from the developer settings page."
        )
    elif isinstance(e, HTTPStatusError) and e.response.status_code == 429:
        msg = "Todoist API rate limit hit. Wait a moment and try again."
    elif isinstance(e, (ConnectError, OSError)):
        msg = "Couldn't reach the Todoist API. Check your internet connection and try again."
    else:
        msg = f"Something went wrong: {e}"

    click.echo(f"Error: {msg}", err=True)
    raise SystemExit(1) from None


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
