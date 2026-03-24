"""Task CLI commands."""

from __future__ import annotations

import sys

import click

from td.cli.errors import TdValidationError
from td.cli.output import OutputFormatter
from td.core.client import get_client
from td.core.projects import get_inbox_project, resolve_project
from td.core.tasks import (
    complete_task,
    create_task,
    edit_task,
    list_tasks,
    quick_add,
    remove_task,
)


def _get_formatter(ctx: click.Context) -> OutputFormatter:
    return ctx.obj["formatter"]  # type: ignore[no-any-return]


@click.command()
@click.argument("content", nargs=-1, required=True)
@click.option("-p", "--project", "project_name", help="Project name or ID.")
@click.option(
    "--priority",
    type=click.IntRange(1, 4),
    help="Priority 1-4 (1=urgent).",
)
@click.option("-d", "--due", help="Due date (e.g., 'tomorrow', '2026-04-01').")
@click.option("-l", "--label", "labels", multiple=True, help="Label (repeatable).")
@click.option("--desc", "description", help="Task description.")
@click.option(
    "--idempotent",
    is_flag=True,
    help="Skip if identical task already exists.",
)
@click.pass_context
def add(
    ctx: click.Context,
    content: tuple[str, ...],
    project_name: str | None,
    priority: int | None,
    due: str | None,
    labels: tuple[str, ...],
    description: str | None,
    idempotent: bool,
) -> None:
    """Create a new task."""
    api = get_client()
    fmt = _get_formatter(ctx)
    text = " ".join(content)

    project_id = None
    if project_name:
        project_id = resolve_project(api, project_name).id

    # Todoist uses inverted priority: 4=urgent, 1=normal
    # We expose 1=urgent to users, map to API values
    api_priority = (5 - priority) if priority else None

    task, created = create_task(
        api,
        text,
        project_id=project_id,
        priority=api_priority,
        due_string=due,
        labels=list(labels) if labels else None,
        description=description,
        idempotent=idempotent,
    )
    fmt.item_created("task", task, created=created)


@click.command(name="ls")
@click.option("-p", "--project", "project_name", help="Filter by project.")
@click.option("-l", "--label", help="Filter by label.")
@click.option("-f", "--filter", "query", help="Todoist filter query.")
@click.pass_context
def ls(
    ctx: click.Context,
    project_name: str | None,
    label: str | None,
    query: str | None,
) -> None:
    """List tasks."""
    api = get_client()
    fmt = _get_formatter(ctx)

    project_id = None
    if project_name:
        project_id = resolve_project(api, project_name).id

    tasks = list_tasks(
        api,
        project_id=project_id,
        label=label,
        filter_query=query,
    )
    fmt.task_list(tasks)


@click.command()
@click.pass_context
def inbox(ctx: click.Context) -> None:
    """Show unprocessed inbox tasks."""
    api = get_client()
    fmt = _get_formatter(ctx)

    project = get_inbox_project(api)
    tasks = list_tasks(api, project_id=project.id)
    fmt.task_list(tasks, title="Inbox")


@click.command()
@click.argument("task_id")
@click.pass_context
def done(ctx: click.Context, task_id: str) -> None:
    """Complete a task."""
    api = get_client()
    fmt = _get_formatter(ctx)

    complete_task(api, task_id)
    fmt.success(f"Completed task {task_id}", {"task_id": task_id})


@click.command()
@click.argument("task_id")
@click.option("--content", help="New content.")
@click.option(
    "--priority",
    type=click.IntRange(1, 4),
    help="Priority 1-4 (1=urgent).",
)
@click.option("-d", "--due", help="New due date.")
@click.option("-l", "--label", "labels", multiple=True, help="Labels (repeatable).")
@click.option("--desc", "description", help="New description.")
@click.pass_context
def edit(
    ctx: click.Context,
    task_id: str,
    content: str | None,
    priority: int | None,
    due: str | None,
    labels: tuple[str, ...],
    description: str | None,
) -> None:
    """Update a task."""
    api = get_client()
    fmt = _get_formatter(ctx)

    api_priority = (5 - priority) if priority else None

    task = edit_task(
        api,
        task_id,
        content=content,
        priority=api_priority,
        due_string=due,
        labels=list(labels) if labels else None,
        description=description,
    )
    fmt.task(task)


@click.command()
@click.argument("task_id")
@click.option("-y", "--yes", is_flag=True, help="Skip confirmation.")
@click.pass_context
def delete(ctx: click.Context, task_id: str, yes: bool) -> None:
    """Delete a task."""
    if not yes:
        if not sys.stdout.isatty():
            raise TdValidationError(
                "Cannot confirm deletion in non-interactive mode.",
                suggestion="Use --yes flag to skip confirmation.",
            )
        if not click.confirm(f"Delete task {task_id}?"):
            click.echo("Aborted.")
            return

    api = get_client()
    fmt = _get_formatter(ctx)
    remove_task(api, task_id)
    fmt.success(f"Deleted task {task_id}", {"task_id": task_id})


@click.command()
@click.argument("text", nargs=-1, required=True)
@click.pass_context
def quick(ctx: click.Context, text: tuple[str, ...]) -> None:
    """Natural language task creation.

    Example: td quick "Buy milk tomorrow p1 #Errands"
    """
    api = get_client()
    fmt = _get_formatter(ctx)

    task = quick_add(api, " ".join(text))
    fmt.item_created("task", task)
