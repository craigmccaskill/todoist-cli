"""Sections CLI command."""

from __future__ import annotations

import click

from td.cli.output import OutputFormatter
from td.core.client import get_client
from td.core.projects import resolve_project
from td.core.sections import _collect_sections


def _get_formatter(ctx: click.Context) -> OutputFormatter:
    return ctx.obj["formatter"]  # type: ignore[no-any-return]


@click.command()
@click.option(
    "-p",
    "--project",
    "project_name",
    required=True,
    help="Project name or ID.",
)
@click.pass_context
def sections(ctx: click.Context, project_name: str) -> None:
    """List sections in a project."""
    api = get_client()
    fmt = _get_formatter(ctx)

    project = resolve_project(api, project_name)
    all_sections = _collect_sections(api, project_id=project.id)
    fmt.section_list(all_sections)
