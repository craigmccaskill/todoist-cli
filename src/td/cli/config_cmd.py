"""Configuration commands: init, completions."""

from __future__ import annotations

import logging
import os
import shutil
import sys
from pathlib import Path

import click
from rich.console import Console
from todoist_api_python.api import TodoistAPI

from td.core.config import TdConfig, get_config_path, load_config, save_config

_TODOIST_SETTINGS_URL = "https://app.todoist.com/app/settings/integrations/developer"

_SUPPORTED_SHELLS = ("bash", "zsh", "fish")

# Completion line templates
_COMPLETION_LINES: dict[str, str] = {
    "bash": 'eval "$(_TD_COMPLETE=bash_source td)"',
    "zsh": 'eval "$(_TD_COMPLETE=zsh_source td)"',
    "fish": "_TD_COMPLETE=fish_source td | source",
}

# Profile file paths (relative to $HOME)
_PROFILE_FILES: dict[str, str] = {
    "bash": ".bashrc",
    "zsh": ".zshrc",
    "fish": ".config/fish/config.fish",
}


def _detect_shell() -> str | None:
    """Detect the current shell from $SHELL."""
    shell_path = os.environ.get("SHELL", "")
    for name in _SUPPORTED_SHELLS:
        if name in shell_path:
            return name
    return None


def _get_profile_path(shell: str) -> Path:
    """Return the profile file path for a given shell."""
    home = Path.home()
    return home / _PROFILE_FILES[shell]


def _is_completion_installed(shell: str) -> tuple[bool, Path]:
    """Check if the completion line is already in the profile file.

    Returns (installed, profile_path).
    """
    profile = _get_profile_path(shell)
    line = _COMPLETION_LINES[shell]
    if profile.exists():
        content = profile.read_text()
        return line in content, profile
    return False, profile


def _require_shell(shell: str | None) -> str:
    """Resolve and validate shell, raising UsageError if unsupported."""
    if shell is None:
        shell = _detect_shell()
    if shell is None:
        supported = ", ".join(_SUPPORTED_SHELLS)
        raise click.UsageError(
            f"Could not detect shell from $SHELL. "
            f"Specify one explicitly with --shell [{supported}]"
        )
    return shell


def _install_completions(shell: str) -> tuple[bool, Path]:
    """Install completion line into profile file.

    Returns (was_installed, profile_path). If already present, returns (False, path).
    """
    profile = _get_profile_path(shell)
    line = _COMPLETION_LINES[shell]

    # Idempotent: skip if already present
    needs_newline = False
    if profile.exists():
        content = profile.read_text()
        if line in content:
            return False, profile
        needs_newline = bool(content) and not content.endswith("\n")
    else:
        # Create parent dirs for fish
        profile.parent.mkdir(parents=True, exist_ok=True)

    # Append the completion line
    with profile.open("a") as f:
        if needs_newline:
            f.write("\n")
        f.write(f"{line}\n")

    return True, profile


def _uninstall_completions(shell: str) -> tuple[bool, Path]:
    """Remove completion line from profile file.

    Returns (was_removed, profile_path). If not present, returns (False, path).
    """
    profile = _get_profile_path(shell)
    line = _COMPLETION_LINES[shell]

    if not profile.exists():
        return False, profile

    content = profile.read_text()
    if line not in content:
        return False, profile

    # Remove the line (and trailing newline)
    new_content = content.replace(f"{line}\n", "")
    # Handle case where line is at end without trailing newline
    new_content = new_content.replace(line, "")
    profile.write_text(new_content)

    return True, profile


def _check_path_collision() -> str | None:
    """Check if another 'td' binary exists on PATH that might conflict.

    Returns a warning message if a collision is detected, None otherwise.
    """
    # Find all 'td' executables on PATH
    td_path = shutil.which("td")
    if td_path is None:
        return None

    # Check all PATH entries for td binaries
    path_dirs = os.environ.get("PATH", "").split(os.pathsep)
    td_locations: list[str] = []
    for d in path_dirs:
        candidate = Path(d) / "td"
        if candidate.exists() and candidate.is_file():
            td_locations.append(str(candidate.resolve()))

    # Deduplicate
    unique_locations = list(dict.fromkeys(td_locations))

    if len(unique_locations) <= 1:
        return None

    # There are multiple td binaries
    # The first one on PATH is what runs when user types 'td'
    first = unique_locations[0]
    # Try to determine which one is "ours"
    # Our td is typically installed in the same prefix as sys.executable
    our_prefix = str(Path(sys.executable).resolve().parent)
    others = [loc for loc in unique_locations if not loc.startswith(our_prefix)]

    if not others:
        return None

    return (
        f'"td" is already on your PATH ({others[0]})\n'
        "  To avoid conflicts, add an alias to your shell profile:\n"
        '    alias todo="td"\n'
        f"  Or ensure {first} points to this installation."
    )


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

    # Offer shell completions
    detected_shell = _detect_shell()
    if detected_shell:
        installed, _profile = _is_completion_installed(detected_shell)
        if not installed:
            click.echo()
            enable = click.confirm("Enable shell completions?", default=True)
            if enable:
                was_installed, profile = _install_completions(detected_shell)
                if was_installed:
                    click.echo(f"Completions added to {profile}")
                    click.echo("Restart your shell or run: source " + str(profile))

    # PATH collision detection
    collision_msg = _check_path_collision()
    if collision_msg:
        click.echo()
        click.echo(f"Warning: {collision_msg}")

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
    elif isinstance(e, ConnectError | OSError):
        msg = "Couldn't reach the Todoist API. Check your internet connection and try again."
    else:
        msg = f"Something went wrong: {e}"

    click.echo(f"Error: {msg}", err=True)
    raise SystemExit(1) from None


@click.group(invoke_without_command=True)
@click.option(
    "--shell",
    type=click.Choice(_SUPPORTED_SHELLS),
    default=None,
    help="Shell to use (auto-detected from $SHELL if omitted).",
)
@click.pass_context
def completions(ctx: click.Context, shell: str | None) -> None:
    """Manage shell tab completions.

    \b
    Without a subcommand, shows completion status for your shell.
    Subcommands: install, uninstall, show
    """
    ctx.ensure_object(dict)
    ctx.obj["shell_override"] = shell

    if ctx.invoked_subcommand is not None:
        return

    # No subcommand: show status
    resolved = shell if shell else _detect_shell()
    if resolved is None:
        supported = ", ".join(_SUPPORTED_SHELLS)
        raise click.UsageError(
            f"Could not detect shell from $SHELL. Specify one with --shell [{supported}]"
        )

    installed, profile = _is_completion_installed(resolved)
    click.echo(f"Shell:  {resolved}")
    if installed:
        click.echo(f"Status: installed ({profile})")
    else:
        click.echo("Status: not installed")
        click.echo()
        click.echo("To enable tab completions, run:")
        click.echo("  td completions install")
        click.echo()
        click.echo(f"This adds a single line to your {profile}. You can remove it anytime with:")
        click.echo("  td completions uninstall")


@completions.command()
@click.pass_context
def install(ctx: click.Context) -> None:
    """Install shell completions into your profile."""
    shell_override = ctx.obj.get("shell_override")
    shell = _require_shell(shell_override)

    was_installed, profile = _install_completions(shell)
    if was_installed:
        click.echo(f"Completions installed for {shell} in {profile}")
        click.echo(f"Restart your shell or run: source {profile}")
    else:
        click.echo(f"Completions already installed in {profile}")


@completions.command()
@click.pass_context
def uninstall(ctx: click.Context) -> None:
    """Remove shell completions from your profile."""
    shell_override = ctx.obj.get("shell_override")
    shell = _require_shell(shell_override)

    was_removed, profile = _uninstall_completions(shell)
    if was_removed:
        click.echo(f"Completions removed from {profile}")
        click.echo(f"Restart your shell or run: source {profile}")
    else:
        click.echo("No completions found to remove.")


@completions.command()
@click.pass_context
def show(ctx: click.Context) -> None:
    """Output the raw completion script."""
    shell_override = ctx.obj.get("shell_override")
    shell = _require_shell(shell_override)

    var = "_TD_COMPLETE"
    if shell == "bash":
        click.echo(f'eval "$({var}=bash_source td)"')
    elif shell == "zsh":
        click.echo(f'eval "$({var}=zsh_source td)"')
    elif shell == "fish":
        click.echo(f"{var}=fish_source td | source")
