"""Sections CLI commands."""

from __future__ import annotations

from typing import cast

import click

from td.cli.completions import _complete_projects
from td.cli.output import OutputFormatter
from td.core.client import get_client
from td.core.projects import resolve_project
from td.core.sections import _collect_sections


def _get_formatter(ctx: click.Context) -> OutputFormatter:
    return cast(OutputFormatter, ctx.obj["formatter"])


@click.command()
@click.option(
    "-p",
    "--project",
    "project_name",
    required=True,
    help="Project name or ID.",
    shell_complete=_complete_projects,
)
@click.pass_context
def sections(ctx: click.Context, project_name: str) -> None:
    """List sections in a project. Requires -p/--project."""
    api = get_client()
    fmt = _get_formatter(ctx)

    project = resolve_project(api, project_name)
    all_sections = _collect_sections(api, project_id=project.id)
    fmt.section_list(all_sections)


@click.command(name="section-add")
@click.argument("name", nargs=-1, required=True)
@click.option(
    "-p",
    "--project",
    "project_name",
    required=True,
    help="Project name or ID.",
    shell_complete=_complete_projects,
)
@click.pass_context
def section_add(ctx: click.Context, name: tuple[str, ...], project_name: str) -> None:
    """Create a new section in a project. Requires -p/--project."""
    api = get_client()
    fmt = _get_formatter(ctx)

    project = resolve_project(api, project_name)
    section = api.add_section(name=" ".join(name), project_id=project.id)
    fmt.item_created("section", section)
