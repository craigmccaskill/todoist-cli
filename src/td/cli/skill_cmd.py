"""Skill management commands for AI agents."""

from __future__ import annotations

from typing import cast

import click

from td.cli.output import OutputFormatter


def _get_formatter(ctx: click.Context) -> OutputFormatter:
    return cast(OutputFormatter, ctx.obj["formatter"])


@click.group(invoke_without_command=True)
@click.pass_context
def skill(ctx: click.Context) -> None:
    """Manage AI agent skills for td.

    \b
    Show status or install/uninstall the td skill for your AI agent:
      td skill                    Show install status
      td skill install            Auto-detect agent and install
      td skill install claude-code  Install for a specific agent
      td skill uninstall          Remove the skill file
    """
    if ctx.invoked_subcommand is not None:
        return

    from td.core.skill import AGENT_TARGETS, detect_agent, is_installed, needs_update

    agent = detect_agent()

    if not agent:
        click.echo("No supported AI agent detected.")
        click.echo("")
        valid = ", ".join(sorted(AGENT_TARGETS.keys()))
        click.echo(f"Supported agents: {valid}")
        click.echo("Install explicitly: td skill install <agent>")
        return

    _, agent_desc = AGENT_TARGETS[agent]
    installed = is_installed(agent)

    if installed:
        from td.core.skill import get_skill_path, installed_version

        ver = installed_version(agent)
        click.echo(f"Agent: {agent_desc}")
        click.echo(f"Status: installed ({get_skill_path(agent)})")
        if ver:
            click.echo(f"Skill version: {ver}")
        if needs_update(agent):
            click.echo("")
            click.echo("Update available — run: td skill update")
        else:
            click.echo("")
            click.echo("To update: td skill update")
            click.echo("To remove: td skill uninstall")
    else:
        click.echo(f"Agent: {agent_desc}")
        click.echo("Status: not installed")
        click.echo("")
        click.echo("To install: td skill install")


@skill.command()
@click.argument("agent", required=False)
@click.pass_context
def install(ctx: click.Context, agent: str | None) -> None:
    """Install td skill for an AI agent.

    \b
    Auto-detects your agent, or specify one:
      td skill install              Auto-detect
      td skill install claude-code  Explicit
    """
    from td.cli import cli as cli_group
    from td.core.skill import (
        AGENT_TARGETS,
        detect_agent,
        generate_skill_content,
        install_skill,
    )
    from td.schema import generate_schema

    fmt = _get_formatter(ctx)

    if not agent:
        agent = detect_agent()
        if not agent:
            valid = ", ".join(sorted(AGENT_TARGETS.keys()))
            raise click.UsageError(
                f"Could not detect an AI agent. Specify one: td skill install [{valid}]"
            )

    if agent not in AGENT_TARGETS:
        valid = ", ".join(sorted(AGENT_TARGETS.keys()))
        raise click.UsageError(f"Unknown agent '{agent}'. Supported: {valid}")

    schema = generate_schema(cli_group)
    content = generate_skill_content(schema)
    path = install_skill(agent, content)

    _, agent_desc = AGENT_TARGETS[agent]
    fmt.success(
        f"Installed td skill for {agent_desc}",
        {"agent": agent, "path": str(path)},
    )


@skill.command()
@click.argument("agent", required=False)
@click.pass_context
def uninstall(ctx: click.Context, agent: str | None) -> None:
    """Remove td skill for an AI agent."""
    from td.core.skill import AGENT_TARGETS, detect_agent, uninstall_skill

    fmt = _get_formatter(ctx)

    if not agent:
        agent = detect_agent()
        if not agent:
            valid = ", ".join(sorted(AGENT_TARGETS.keys()))
            raise click.UsageError(
                f"Could not detect an AI agent. Specify one: td skill uninstall [{valid}]"
            )

    path = uninstall_skill(agent)
    if path:
        _, agent_desc = AGENT_TARGETS[agent]
        fmt.success(
            f"Removed td skill for {agent_desc}",
            {"agent": agent, "path": str(path)},
        )
    else:
        click.echo("Skill not installed. Nothing to remove.")


@skill.command()
@click.argument("agent", required=False)
@click.pass_context
def update(ctx: click.Context, agent: str | None) -> None:
    """Update td skill (regenerate SKILL.md with latest commands)."""
    # Delegate to install — same logic
    ctx.invoke(install, agent=agent)
