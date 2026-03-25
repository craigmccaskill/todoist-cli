"""Review CLI command — interactive inbox processing."""

from __future__ import annotations

import sys

import click

from td.cli.errors import TdValidationError
from td.cli.output import OutputFormatter
from td.core.client import get_client
from td.core.labels import _collect_labels
from td.core.projects import _collect_projects, get_inbox_project, resolve_project
from td.core.tasks import list_tasks, sort_tasks


def _get_formatter(ctx: click.Context) -> OutputFormatter:
    return ctx.obj["formatter"]  # type: ignore[no-any-return]


@click.command()
@click.option("-p", "--project", "project_name", help="Review a specific project.")
@click.option("-f", "--filter", "query", help="Review tasks matching a filter.")
@click.pass_context
def review(
    ctx: click.Context,
    project_name: str | None,
    query: str | None,
) -> None:
    """Interactive inbox review — process tasks one by one.

    Defaults to inbox tasks. Use -p for a project or -f for a filter.
    """
    if not sys.stdout.isatty():
        raise TdValidationError(
            "td review requires an interactive terminal.",
            suggestion="Run in a terminal, not piped.",
        )

    from td.tui import is_available

    if not is_available():
        raise TdValidationError(
            "Interactive features require textual.",
            suggestion='Install with: pip install "todoist-cli[interactive]"',
        )

    api = get_client()

    # Determine task source
    if query:
        tasks = list_tasks(api, filter_query=query)
        title = f"Review: {query}"
    elif project_name:
        project = resolve_project(api, project_name)
        tasks = list_tasks(api, project_id=project.id)
        title = f"Review: {project.name}"
    else:
        inbox = get_inbox_project(api)
        tasks = list_tasks(api, project_id=inbox.id)
        title = "Inbox Review"

    tasks = sort_tasks(tasks, "priority")

    if not tasks:
        fmt = _get_formatter(ctx)
        fmt.success("Nothing to review!")
        return

    # Gather projects and labels for pickers
    projects = [{"id": p.id, "name": p.name} for p in _collect_projects(api)]
    labels = [lbl.name for lbl in _collect_labels(api)]

    # Launch TUI
    from td.tui.review import ReviewApp

    app = ReviewApp(api, tasks, projects, labels, title=title)
    stats = app.run()

    # Print summary
    if stats:
        click.echo()
        click.echo("━━━ Review complete ━━━")
        click.echo()
        click.echo(
            f"  {len(stats.updated)} updated · "
            f"{len(stats.completed)} completed · "
            f"{stats.skipped} remaining"
        )
        if stats.updated:
            click.echo()
            click.echo("  Updated:")
            for name in stats.updated:
                click.echo(f"    {name}")
        if stats.completed:
            click.echo()
            click.echo("  Completed:")
            for name in stats.completed:
                click.echo(f"    {name}")
        click.echo()
