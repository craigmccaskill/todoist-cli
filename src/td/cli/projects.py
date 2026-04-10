"""Projects CLI command."""

from __future__ import annotations

from typing import cast

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


@click.command()
@click.option("-s", "--search", help="Search projects by name.")
@click.pass_context
def projects(ctx: click.Context, search: str | None) -> None:
    """List all projects. Use -s to search by name."""
    api = get_client()
    fmt = _get_formatter(ctx)

    if search:
        all_projects = [p for page in api.search_projects(query=search) for p in page]
    else:
        all_projects = _collect_projects(api)

    fmt.project_list(all_projects)


@click.command(name="project-add")
@click.argument("name", nargs=-1, required=True)
@click.option(
    "--parent",
    "parent_name",
    help="Parent project name or ID (for sub-projects).",
)
@click.option("--favorite", is_flag=True, help="Mark as favorite.")
@click.pass_context
def project_add(
    ctx: click.Context,
    name: tuple[str, ...],
    parent_name: str | None,
    favorite: bool,
) -> None:
    """Create a new project."""
    api = get_client()
    fmt = _get_formatter(ctx)

    parent_id = None
    if parent_name:
        parent_id = resolve_project(api, parent_name).id

    project = create_project(
        api,
        " ".join(name),
        parent_id=parent_id,
        is_favorite=favorite,
    )
    fmt.item_created("project", project)


@click.command(name="project-edit")
@click.argument("ref", nargs=-1, required=True)
@click.option("--name", help="New project name.")
@click.option("--color", help="New project color.")
@click.pass_context
def project_edit(
    ctx: click.Context,
    ref: tuple[str, ...],
    name: str | None,
    color: str | None,
) -> None:
    """Rename or recolor a project. Ref is a name or ID.

    \b
    Examples:
      td project-edit Work --name "Work stuff"
      td project-edit Personal --color blue
    """
    api = get_client()
    fmt = _get_formatter(ctx)

    if not name and not color:
        raise TdValidationError(
            "Nothing to update.",
            suggestion="Provide --name and/or --color.",
        )

    project = resolve_project(api, " ".join(ref))
    updated = update_project(api, project.id, name=name, color=color)
    fmt.success(
        f"Updated project: {updated.name}",
        {"project_id": updated.id, "name": updated.name},
    )


@click.command(name="project-delete")
@click.argument("ref", nargs=-1, required=True)
@click.option("-y", "--yes", is_flag=True, help="Skip confirmation.")
@click.pass_context
def project_delete(ctx: click.Context, ref: tuple[str, ...], yes: bool) -> None:
    """Delete a project. Ref is a name or ID.

    \b
    Examples:
      td project-delete "Old Project" -y
    """
    api = get_client()
    fmt = _get_formatter(ctx)

    project = resolve_project(api, " ".join(ref))
    if not yes and not click.confirm(f'Delete project "{project.name}"?', default=False):
        click.echo("Aborted.")
        return

    delete_project(api, project.id)
    fmt.success(
        f"Deleted project: {project.name}",
        {"project_id": project.id, "name": project.name},
    )


@click.command(name="project-archive")
@click.argument("ref", nargs=-1, required=True)
@click.pass_context
def project_archive(ctx: click.Context, ref: tuple[str, ...]) -> None:
    """Archive a project. Ref is a name or ID.

    \b
    Examples:
      td project-archive "Old Project"
    """
    api = get_client()
    fmt = _get_formatter(ctx)

    project = resolve_project(api, " ".join(ref))
    archive_project(api, project.id)
    fmt.success(
        f"Archived project: {project.name}",
        {"project_id": project.id, "name": project.name},
    )


@click.command(name="project-unarchive")
@click.argument("ref", nargs=-1, required=True)
@click.pass_context
def project_unarchive(ctx: click.Context, ref: tuple[str, ...]) -> None:
    """Unarchive a project. Ref is a name or ID.

    \b
    Examples:
      td project-unarchive "Old Project"
    """
    api = get_client()
    fmt = _get_formatter(ctx)

    project = resolve_project(api, " ".join(ref))
    unarchive_project(api, project.id)
    fmt.success(
        f"Unarchived project: {project.name}",
        {"project_id": project.id, "name": project.name},
    )
