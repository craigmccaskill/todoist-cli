"""Sections CLI commands.

Public surface: the ``section`` Click group (``add``, ``edit``,
``delete``, ``list``) plus the permanent flat plural alias ``sections``.

Hidden deprecated shims (``section-add``, ``section-edit``,
``section-delete``) keep old invocations working through v0.13.0 with a
stderr warning. They will be removed in v0.14.0. See ADR-0009.
"""

from __future__ import annotations

from collections import defaultdict
from typing import Any, cast

import click
from todoist_api_python.models import Section

from td.cli.completions import _complete_projects
from td.cli.output import OutputFormatter
from td.core.client import get_client
from td.core.projects import get_project_name_map, resolve_project
from td.core.sections import _collect_sections, delete_section, resolve_section, update_section


def _get_formatter(ctx: click.Context) -> OutputFormatter:
    return cast(OutputFormatter, ctx.obj["formatter"])


def _list_sections(api: Any, fmt: OutputFormatter, project_name: str | None) -> None:
    """Shared listing implementation for ``td sections`` and ``td section list``."""
    if project_name:
        project = resolve_project(api, project_name)
        all_sections = _collect_sections(api, project_id=project.id)
        fmt.section_list(all_sections)
        return

    all_sections = _collect_sections(api)
    if not all_sections:
        fmt.section_list([])
        return
    pnames = get_project_name_map(api)
    grouped: dict[str, list[Section]] = defaultdict(list)
    for s in all_sections:
        grouped[s.project_id].append(s)
    fmt.section_list_grouped(grouped, pnames)


def _deprecation_notice(old: str, new: str) -> str:
    return f"Note: td {old} is now td {new}. The old name will be removed in v0.14.0."


# ---------------------------------------------------------------------------
# Permanent flat plural alias
# ---------------------------------------------------------------------------


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
    _list_sections(get_client(), _get_formatter(ctx), project_name)


# ---------------------------------------------------------------------------
# section entity group (primary surface per ADR-0009)
# ---------------------------------------------------------------------------


@click.group(name="section", invoke_without_command=True)
@click.pass_context
def section(ctx: click.Context) -> None:
    """Manage Todoist sections (add, edit, delete, list)."""
    if ctx.invoked_subcommand is None:
        ctx.invoke(_section_list, project_name=None)


@section.command(name="list")
@click.option(
    "-p",
    "--project",
    "project_name",
    help="Scope to a project. Without this, lists all sections grouped by project.",
    shell_complete=_complete_projects,
)
@click.pass_context
def _section_list(ctx: click.Context, project_name: str | None) -> None:
    """List sections, optionally scoped to a project."""
    _list_sections(get_client(), _get_formatter(ctx), project_name)


@section.command(name="add")
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
def _section_add(ctx: click.Context, name: tuple[str, ...], project_name: str) -> None:
    """Create a new section in a project. Requires -p/--project.

    \b
    Examples:
      td section add "Draft posts" -p Blog
    """
    api = get_client()
    fmt = _get_formatter(ctx)

    project = resolve_project(api, project_name)
    sec = api.add_section(name=" ".join(name), project_id=project.id)
    fmt.item_created("section", sec)


@section.command(name="edit")
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
def _section_edit(
    ctx: click.Context,
    ref: tuple[str, ...],
    name: str,
    project_name: str | None,
) -> None:
    """Rename a section. Use -p to scope to a project.

    \b
    Examples:
      td section edit "In Progress" --name "Active" -p Work
    """
    api = get_client()
    fmt = _get_formatter(ctx)

    project_id = None
    if project_name:
        project_id = resolve_project(api, project_name).id

    sec = resolve_section(api, " ".join(ref), project_id=project_id)
    updated = update_section(api, sec.id, name=name)
    fmt.success(
        f"Updated section: {updated.name}",
        {"section_id": updated.id, "name": updated.name},
    )


@section.command(name="delete")
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
def _section_delete(
    ctx: click.Context,
    ref: tuple[str, ...],
    yes: bool,
    project_name: str | None,
) -> None:
    """Delete a section. Use -p to scope to a project.

    \b
    Examples:
      td section delete "Old Section" -p Work -y
    """
    api = get_client()
    fmt = _get_formatter(ctx)

    project_id = None
    if project_name:
        project_id = resolve_project(api, project_name).id

    sec = resolve_section(api, " ".join(ref), project_id=project_id)
    if not yes and not click.confirm(f'Delete section "{sec.name}"?', default=False):
        click.echo("Aborted.")
        return

    delete_section(api, sec.id)
    fmt.success(
        f"Deleted section: {sec.name}",
        {"section_id": sec.id, "name": sec.name},
    )


# ---------------------------------------------------------------------------
# Hidden deprecated aliases (removed in v0.14.0)
# ---------------------------------------------------------------------------


@click.command(name="section-add", hidden=True)
@click.argument("name", nargs=-1, required=True)
@click.option(
    "-p",
    "--project",
    "project_name",
    required=True,
    shell_complete=_complete_projects,
)
@click.pass_context
def section_add(ctx: click.Context, name: tuple[str, ...], project_name: str) -> None:
    """Deprecated: use ``td section add``."""
    click.echo(_deprecation_notice("section-add", "section add"), err=True)
    ctx.invoke(_section_add, name=name, project_name=project_name)


@click.command(name="section-edit", hidden=True)
@click.argument("ref", nargs=-1, required=True)
@click.option("--name", required=True)
@click.option(
    "-p",
    "--project",
    "project_name",
    shell_complete=_complete_projects,
)
@click.pass_context
def section_edit(
    ctx: click.Context,
    ref: tuple[str, ...],
    name: str,
    project_name: str | None,
) -> None:
    """Deprecated: use ``td section edit``."""
    click.echo(_deprecation_notice("section-edit", "section edit"), err=True)
    ctx.invoke(_section_edit, ref=ref, name=name, project_name=project_name)


@click.command(name="section-delete", hidden=True)
@click.argument("ref", nargs=-1, required=True)
@click.option("-y", "--yes", is_flag=True)
@click.option(
    "-p",
    "--project",
    "project_name",
    shell_complete=_complete_projects,
)
@click.pass_context
def section_delete(
    ctx: click.Context,
    ref: tuple[str, ...],
    yes: bool,
    project_name: str | None,
) -> None:
    """Deprecated: use ``td section delete``."""
    click.echo(_deprecation_notice("section-delete", "section delete"), err=True)
    ctx.invoke(_section_delete, ref=ref, yes=yes, project_name=project_name)
