"""Projects CLI command."""

from __future__ import annotations

from typing import cast

import click

from td.cli.output import OutputFormatter
from td.core.client import get_client
from td.core.projects import _collect_projects, create_project, resolve_project


def _get_formatter(ctx: click.Context) -> OutputFormatter:
    return cast(OutputFormatter, ctx.obj["formatter"])


@click.command()
@click.option("-s", "--search", help="Search projects by name.")
@click.pass_context
def projects(ctx: click.Context, search: str | None) -> None:
    """List all projects."""
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
