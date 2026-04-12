"""Projects CLI commands.

Public command surface is the ``project`` Click group defined in this
module (with ``add``, ``edit``, ``delete``, ``archive``, ``unarchive``,
``list`` subcommands) plus the permanent flat plural alias ``projects``
for the common "show me the list" case.

The old hyphenated flat commands (``project-add`` etc.) are kept as
hidden deprecated shims that emit a stderr notice and delegate to the
new subcommands. They will be removed in v0.14.0. See ADR-0009 for the
full grammar decision.
"""

from __future__ import annotations

from typing import Any, cast

import click

from td.cli.errors import TdValidationError
from td.cli.output import OutputFormatter
from td.core.client import get_client
from td.core.projects import (
    _collect_projects,
    archive_project,
    create_project,
    delete_project,
    resolve_project,
    unarchive_project,
    update_project,
)


def _get_formatter(ctx: click.Context) -> OutputFormatter:
    return cast(OutputFormatter, ctx.obj["formatter"])


def _list_projects(api: Any, fmt: OutputFormatter, search: str | None) -> None:
    """Shared listing implementation used by both ``td projects`` and ``td project list``."""
    if search:
        all_projects = [p for page in api.search_projects(query=search) for p in page]
    else:
        all_projects = _collect_projects(api)
    fmt.project_list(all_projects)


# ---------------------------------------------------------------------------
# Permanent flat plural alias for the list case.
#
# ADR-0001 cites ``td sections Blog`` as a canonical example of "accept
# what the user means, not what the system needs." Plural list commands
# stay as permanent shortcuts and are not deprecated by ADR-0009.
# ---------------------------------------------------------------------------


@click.command()
@click.option("-s", "--search", help="Search projects by name.")
@click.pass_context
def projects(ctx: click.Context, search: str | None) -> None:
    """List all projects. Use -s to search by name."""
    _list_projects(get_client(), _get_formatter(ctx), search)


# ---------------------------------------------------------------------------
# project entity group (primary surface per ADR-0009)
# ---------------------------------------------------------------------------


@click.group(name="project", invoke_without_command=True)
@click.pass_context
def project(ctx: click.Context) -> None:
    """Manage Todoist projects (add, edit, delete, archive, unarchive, list)."""
    if ctx.invoked_subcommand is None:
        ctx.invoke(_project_list, search=None)


@project.command(name="list")
@click.option("-s", "--search", help="Search projects by name.")
@click.pass_context
def _project_list(ctx: click.Context, search: str | None) -> None:
    """List all projects. Use -s to search by name."""
    _list_projects(get_client(), _get_formatter(ctx), search)


@project.command(name="add")
@click.argument("name", nargs=-1, required=True)
@click.option(
    "--parent",
    "parent_name",
    help="Parent project name or ID (for sub-projects).",
)
@click.option("--favorite", is_flag=True, help="Mark as favorite.")
@click.pass_context
def _project_add(
    ctx: click.Context,
    name: tuple[str, ...],
    parent_name: str | None,
    favorite: bool,
) -> None:
    """Create a new project.

    \b
    Examples:
      td project add "Home improvements"
      td project add "Q2 OKRs" --parent Work
    """
    api = get_client()
    fmt = _get_formatter(ctx)

    parent_id = None
    if parent_name:
        parent_id = resolve_project(api, parent_name).id

    proj = create_project(
        api,
        " ".join(name),
        parent_id=parent_id,
        is_favorite=favorite,
    )
    fmt.item_created("project", proj)


@project.command(name="edit")
@click.argument("ref", nargs=-1, required=True)
@click.option("--name", help="New project name.")
@click.option("--color", help="New project color.")
@click.pass_context
def _project_edit(
    ctx: click.Context,
    ref: tuple[str, ...],
    name: str | None,
    color: str | None,
) -> None:
    """Rename or recolor a project. Ref is a name or ID.

    \b
    Examples:
      td project edit Work --name "Work stuff"
      td project edit Personal --color blue
    """
    api = get_client()
    fmt = _get_formatter(ctx)

    if not name and not color:
        raise TdValidationError(
            "Nothing to update.",
            suggestion="Provide --name and/or --color.",
        )

    proj = resolve_project(api, " ".join(ref))
    updated = update_project(api, proj.id, name=name, color=color)
    fmt.success(
        f"Updated project: {updated.name}",
        {"project_id": updated.id, "name": updated.name},
    )


@project.command(name="delete")
@click.argument("ref", nargs=-1, required=True)
@click.option("-y", "--yes", is_flag=True, help="Skip confirmation.")
@click.pass_context
def _project_delete(ctx: click.Context, ref: tuple[str, ...], yes: bool) -> None:
    """Delete a project. Ref is a name or ID.

    \b
    Examples:
      td project delete "Old Project" -y
    """
    api = get_client()
    fmt = _get_formatter(ctx)

    proj = resolve_project(api, " ".join(ref))
    if not yes and not click.confirm(f'Delete project "{proj.name}"?', default=False):
        click.echo("Aborted.")
        return

    delete_project(api, proj.id)
    fmt.success(
        f"Deleted project: {proj.name}",
        {"project_id": proj.id, "name": proj.name},
    )


@project.command(name="archive")
@click.argument("ref", nargs=-1, required=True)
@click.pass_context
def _project_archive(ctx: click.Context, ref: tuple[str, ...]) -> None:
    """Archive a project. Ref is a name or ID.

    \b
    Examples:
      td project archive "Old Project"
    """
    api = get_client()
    fmt = _get_formatter(ctx)

    proj = resolve_project(api, " ".join(ref))
    archive_project(api, proj.id)
    fmt.success(
        f"Archived project: {proj.name}",
        {"project_id": proj.id, "name": proj.name},
    )


@project.command(name="unarchive")
@click.argument("ref", nargs=-1, required=True)
@click.pass_context
def _project_unarchive(ctx: click.Context, ref: tuple[str, ...]) -> None:
    """Unarchive a project. Ref is a name or ID.

    \b
    Examples:
      td project unarchive "Old Project"
    """
    api = get_client()
    fmt = _get_formatter(ctx)

    proj = resolve_project(api, " ".join(ref))
    unarchive_project(api, proj.id)
    fmt.success(
        f"Unarchived project: {proj.name}",
        {"project_id": proj.id, "name": proj.name},
    )


# ---------------------------------------------------------------------------
# Hidden deprecated aliases (removed in v0.14.0 per ADR-0009).
#
# Each shim emits a one-line stderr notice and delegates via ``ctx.invoke``
# to the new subcommand. Hidden from ``--help`` and from ``td schema``.
# ---------------------------------------------------------------------------


def _deprecation_notice(old: str, new: str) -> str:
    return f"Note: td {old} is now td {new}. The old name will be removed in v0.14.0."


@click.command(name="project-add", hidden=True)
@click.argument("name", nargs=-1, required=True)
@click.option("--parent", "parent_name")
@click.option("--favorite", is_flag=True)
@click.pass_context
def project_add(
    ctx: click.Context,
    name: tuple[str, ...],
    parent_name: str | None,
    favorite: bool,
) -> None:
    """Deprecated: use ``td project add``."""
    click.echo(_deprecation_notice("project-add", "project add"), err=True)
    ctx.invoke(_project_add, name=name, parent_name=parent_name, favorite=favorite)


@click.command(name="project-edit", hidden=True)
@click.argument("ref", nargs=-1, required=True)
@click.option("--name")
@click.option("--color")
@click.pass_context
def project_edit(
    ctx: click.Context,
    ref: tuple[str, ...],
    name: str | None,
    color: str | None,
) -> None:
    """Deprecated: use ``td project edit``."""
    click.echo(_deprecation_notice("project-edit", "project edit"), err=True)
    ctx.invoke(_project_edit, ref=ref, name=name, color=color)


@click.command(name="project-delete", hidden=True)
@click.argument("ref", nargs=-1, required=True)
@click.option("-y", "--yes", is_flag=True)
@click.pass_context
def project_delete(ctx: click.Context, ref: tuple[str, ...], yes: bool) -> None:
    """Deprecated: use ``td project delete``."""
    click.echo(_deprecation_notice("project-delete", "project delete"), err=True)
    ctx.invoke(_project_delete, ref=ref, yes=yes)


@click.command(name="project-archive", hidden=True)
@click.argument("ref", nargs=-1, required=True)
@click.pass_context
def project_archive(ctx: click.Context, ref: tuple[str, ...]) -> None:
    """Deprecated: use ``td project archive``."""
    click.echo(_deprecation_notice("project-archive", "project archive"), err=True)
    ctx.invoke(_project_archive, ref=ref)


@click.command(name="project-unarchive", hidden=True)
@click.argument("ref", nargs=-1, required=True)
@click.pass_context
def project_unarchive(ctx: click.Context, ref: tuple[str, ...]) -> None:
    """Deprecated: use ``td project unarchive``."""
    click.echo(_deprecation_notice("project-unarchive", "project unarchive"), err=True)
    ctx.invoke(_project_unarchive, ref=ref)
