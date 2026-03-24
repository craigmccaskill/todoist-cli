"""Projects CLI command."""

from __future__ import annotations

import click

from td.cli.output import OutputFormatter
from td.core.client import get_client
from td.core.projects import _collect_projects


def _get_formatter(ctx: click.Context) -> OutputFormatter:
    return ctx.obj["formatter"]  # type: ignore[no-any-return]


@click.command()
@click.option("-s", "--search", help="Search projects by name.")
@click.pass_context
def projects(ctx: click.Context, search: str | None) -> None:
    """List all projects."""
    api = get_client()
    fmt = _get_formatter(ctx)

    if search:

        all_projects = [
            p
            for page in api.search_projects(query=search)
            for p in page
        ]
    else:
        all_projects = _collect_projects(api)

    fmt.project_list(all_projects)
