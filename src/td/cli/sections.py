"""Sections CLI commands."""

from __future__ import annotations

from collections import defaultdict
from typing import cast

import click
from todoist_api_python.models import Section

from td.cli.completions import _complete_projects
from td.cli.output import OutputFormatter
from td.core.client import get_client
from td.core.projects import get_project_name_map, resolve_project
from td.core.sections import _collect_sections, delete_section, resolve_section, update_section


def _get_formatter(ctx: click.Context) -> OutputFormatter:
    return cast(OutputFormatter, ctx.obj["formatter"])


@click.command()
@click.option(
    "-p",
    "--project",
    "project_name",
    help="Scope to a project. Without this, lists all sections grouped by project.",
    shell_complete=_complete_projects,
)
@click.pass_context
def sections(ctx: click.Context, project_name: str | None) -> None:
    """List sections, optionally scoped to a project."""
    api = get_client()
    fmt = _get_formatter(ctx)

    if project_name:
        project = resolve_project(api, project_name)
        all_sections = _collect_sections(api, project_id=project.id)
        fmt.section_list(all_sections)
    else:
        all_sections = _collect_sections(api)
        if not all_sections:
            fmt.section_list([])
            return
        pnames = get_project_name_map(api)
        grouped: dict[str, list[Section]] = defaultdict(list)
        for s in all_sections:
            grouped[s.project_id].append(s)
        fmt.section_list_grouped(grouped, pnames)


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


@click.command(name="section-edit")
@click.argument("ref", nargs=-1, required=True)
@click.option("--name", required=True, help="New section name.")
@click.option(
    "-p",
    "--project",
    "project_name",
    help="Project to scope section lookup.",
    shell_complete=_complete_projects,
)
@click.pass_context
def section_edit(
    ctx: click.Context,
    ref: tuple[str, ...],
    name: str,
    project_name: str | None,
) -> None:
    """Rename a section. Use -p to scope to a project.

    \b
    Examples:
      td section-edit "In Progress" --name "Active" -p Work
    """
    api = get_client()
    fmt = _get_formatter(ctx)

    project_id = None
    if project_name:
        project_id = resolve_project(api, project_name).id

    section = resolve_section(api, " ".join(ref), project_id=project_id)
    updated = update_section(api, section.id, name=name)
    fmt.success(
        f"Updated section: {updated.name}",
        {"section_id": updated.id, "name": updated.name},
    )


@click.command(name="section-delete")
@click.argument("ref", nargs=-1, required=True)
@click.option("-y", "--yes", is_flag=True, help="Skip confirmation.")
@click.option(
    "-p",
    "--project",
    "project_name",
    help="Project to scope section lookup.",
    shell_complete=_complete_projects,
)
@click.pass_context
def section_delete(
    ctx: click.Context,
    ref: tuple[str, ...],
    yes: bool,
    project_name: str | None,
) -> None:
    """Delete a section. Use -p to scope to a project.

    \b
    Examples:
      td section-delete "Old Section" -p Work -y
    """
    api = get_client()
    fmt = _get_formatter(ctx)

    project_id = None
    if project_name:
        project_id = resolve_project(api, project_name).id

    section = resolve_section(api, " ".join(ref), project_id=project_id)
    if not yes and not click.confirm(f'Delete section "{section.name}"?', default=False):
        click.echo("Aborted.")
        return

    delete_section(api, section.id)
    fmt.success(
        f"Deleted section: {section.name}",
        {"section_id": section.id, "name": section.name},
    )
