"""Task CLI commands."""

from __future__ import annotations

import sys
from typing import Any

import click

from td.cli.errors import TdValidationError
from td.cli.output import OutputFormatter
from td.core.cache import resolve_task_ref
from td.core.client import get_client
from td.core.config import load_config
from td.core.projects import get_inbox_project, get_project_name_map, resolve_project
from td.core.sections import resolve_section
from td.core.tasks import (
    SORT_OPTIONS,
    complete_task,
    create_task,
    edit_task,
    find_task_by_content,
    list_tasks,
    quick_add,
    remove_task,
    sort_tasks,
    uncomplete_task,
)


def _get_formatter(ctx: click.Context) -> OutputFormatter:
    return ctx.obj["formatter"]  # type: ignore[no-any-return]


def _resolve_task(ref: str, api: Any = None) -> str:
    """Resolve a task reference: row number → content match → task ID.

    1. If ref is a digit, try cached row number
    2. If api is provided and ref looks like text, try content matching
    3. Fall through to raw ref (assumed task ID)
    """
    # Step 1: row number from cache
    resolved = resolve_task_ref(ref)
    if resolved != ref:
        return resolved

    # Step 2: content match (if ref doesn't look like a typical ID)
    if api and not ref.isdigit() and len(ref) > 2:
        matches = find_task_by_content(api, ref)
        if len(matches) == 1:
            return matches[0].id
        if len(matches) > 1 and sys.stdout.isatty():
            click.echo(f"Multiple matches for '{ref}':")
            for i, t in enumerate(matches[:10], 1):
                due = f"  {t.due.string}" if t.due else ""
                click.echo(f"  {i}  {t.content}{due}")
            choice = click.prompt(
                "Which task?",
                type=click.IntRange(1, min(len(matches), 10)),
            )
            task_id: str = matches[choice - 1].id
            return task_id
        if len(matches) > 1:
            # Non-interactive: return error-like info
            from td.cli.errors import TdValidationError

            task_list = ", ".join(f"'{t.content}'" for t in matches[:5])
            raise TdValidationError(
                f"Multiple tasks match '{ref}': {task_list}",
                suggestion="Be more specific or use a task ID.",
            )

    # Step 3: pass through as task ID
    return ref


def _read_stdin() -> str | None:
    """Read from stdin if not a TTY (piped input)."""
    if not sys.stdin.isatty():
        return sys.stdin.read().strip() or None
    return None


@click.command()
@click.argument("content", nargs=-1)
@click.option("-p", "--project", "project_name", help="Project name or ID.")
@click.option(
    "--priority",
    type=click.IntRange(1, 4),
    help="Priority: 1=urgent, 2=high, 3=medium, 4=low.",
)
@click.option("-d", "--due", help="Due date (e.g., 'tomorrow', '2026-04-01').")
@click.option("-l", "--label", "labels", multiple=True, help="Label (repeatable).")
@click.option("--desc", "description", help="Task description.")
@click.option(
    "-s",
    "--section",
    "section_name",
    help="Section name (requires --project).",
)
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
    section_name: str | None,
    idempotent: bool,
) -> None:
    """Create a new task. Reads from stdin if no content argument."""
    api = get_client()
    fmt = _get_formatter(ctx)
    text = " ".join(content) if content else (_read_stdin() or "")
    if not text:
        raise TdValidationError(
            "No task content provided.",
            suggestion="Provide content as an argument or pipe via stdin.",
        )

    if section_name and not project_name:
        raise TdValidationError(
            "--section requires --project.",
            suggestion="Specify a project with -p to use --section.",
        )

    project_id = None
    if project_name:
        project_id = resolve_project(api, project_name).id

    section_id = None
    if section_name and project_id:
        section_id = resolve_section(api, section_name, project_id=project_id).id

    # Todoist uses inverted priority: 4=urgent, 1=normal
    # We expose 1=urgent to users, map to API values
    api_priority = (5 - priority) if priority else None

    task, created = create_task(
        api,
        text,
        project_id=project_id,
        section_id=section_id,
        priority=api_priority,
        due_string=due,
        labels=list(labels) if labels else None,
        description=description,
        idempotent=idempotent,
    )
    fmt.item_created("task", task, created=created)


def _resolve_sort(sort: str | None) -> str:
    """Resolve sort order from flag, env, or config."""
    if sort:
        return sort
    config = load_config()
    return config.default_sort


@click.command(name="ls")
@click.option("-p", "--project", "project_name", help="Filter by project.")
@click.option("-l", "--label", help="Filter by label.")
@click.option("-f", "--filter", "query", help="Todoist filter query.")
@click.option(
    "--all",
    "show_all",
    is_flag=True,
    help="Show all tasks (default: today + overdue).",
)
@click.option("--ids", is_flag=True, help="Output only task IDs, one per line.")
@click.option(
    "-s",
    "--sort",
    "sort_by",
    type=click.Choice(SORT_OPTIONS),
    help="Sort order (default: priority).",
)
@click.option("--reverse", "reverse_sort", is_flag=True, help="Reverse sort order.")
@click.pass_context
def ls(
    ctx: click.Context,
    project_name: str | None,
    label: str | None,
    query: str | None,
    show_all: bool,
    ids: bool,
    sort_by: str | None,
    reverse_sort: bool,
) -> None:
    """List tasks. Defaults to today + overdue unless filtered."""
    api = get_client()
    fmt = _get_formatter(ctx)

    project_id = None
    if project_name:
        project_id = resolve_project(api, project_name).id

    # Default to today + overdue when no filters specified
    if not query and not project_name and not label and not show_all:
        query = "overdue | today"

    tasks = list_tasks(
        api,
        project_id=project_id,
        label=label,
        filter_query=query,
    )
    tasks = sort_tasks(tasks, _resolve_sort(sort_by), reverse=reverse_sort)

    if ids:
        for task in tasks:
            click.echo(task.id)
    else:
        pnames = get_project_name_map(api)
        fmt.task_list(tasks, project_names=pnames)


@click.command()
@click.pass_context
def inbox(ctx: click.Context) -> None:
    """Show unprocessed inbox tasks."""
    api = get_client()
    fmt = _get_formatter(ctx)

    project = get_inbox_project(api)
    tasks = list_tasks(api, project_id=project.id)
    tasks = sort_tasks(tasks, _resolve_sort(None))
    fmt.task_list(tasks, title="Inbox")


@click.command()
@click.option(
    "-s",
    "--sort",
    "sort_by",
    type=click.Choice(SORT_OPTIONS),
    help="Sort order (default: priority).",
)
@click.option("--reverse", "reverse_sort", is_flag=True, help="Reverse sort order.")
@click.pass_context
def today(ctx: click.Context, sort_by: str | None, reverse_sort: bool) -> None:
    """Show tasks due today and overdue — your morning dashboard."""
    api = get_client()
    fmt = _get_formatter(ctx)

    tasks = list_tasks(api, filter_query="overdue | today")
    tasks = sort_tasks(tasks, _resolve_sort(sort_by), reverse=reverse_sort)
    pnames = get_project_name_map(api)
    fmt.task_list(tasks, title="Today", project_names=pnames)


@click.command(name="next")
@click.option("-p", "--project", "project_name", help="Scope to a project.")
@click.pass_context
def next_task(ctx: click.Context, project_name: str | None) -> None:
    """Show your highest priority task — what to work on now."""
    api = get_client()
    fmt = _get_formatter(ctx)

    project_id = None
    if project_name:
        project_id = resolve_project(api, project_name).id

    tasks = list_tasks(api, filter_query="overdue | today")
    if project_id:
        tasks = [t for t in tasks if t.project_id == project_id]
    tasks = sort_tasks(tasks, "priority")

    if tasks:
        fmt.task(tasks[0])
    else:
        fmt.success("Nothing to do right now.")


@click.command()
@click.option(
    "--week",
    is_flag=True,
    help="Show completed this week (default: today).",
)
@click.pass_context
def log(ctx: click.Context, week: bool) -> None:
    """Show completed tasks — your end-of-day review."""
    from datetime import datetime, timedelta

    api = get_client()
    fmt = _get_formatter(ctx)

    now = datetime.now().astimezone()
    if week:
        # Monday of this week
        since = (now - timedelta(days=now.weekday())).replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        title = "Completed this week"
    else:
        since = now.replace(hour=0, minute=0, second=0, microsecond=0)
        title = "Completed today"

    completed = [
        t
        for page in api.get_completed_tasks_by_completion_date(since=since, until=now)
        for t in page
    ]
    fmt.task_list(completed, title=title)


@click.command()
@click.argument("project_name")
@click.option(
    "-s",
    "--sort",
    "sort_by",
    type=click.Choice(SORT_OPTIONS),
    help="Sort order (default: priority).",
)
@click.option("--reverse", "reverse_sort", is_flag=True, help="Reverse sort order.")
@click.pass_context
def focus(
    ctx: click.Context,
    project_name: str,
    sort_by: str | None,
    reverse_sort: bool,
) -> None:
    """Focus on a single project — deep work mode."""
    api = get_client()
    fmt = _get_formatter(ctx)

    project = resolve_project(api, project_name)
    tasks = list_tasks(api, project_id=project.id)
    tasks = sort_tasks(tasks, _resolve_sort(sort_by), reverse=reverse_sort)
    fmt.task_list(tasks, title=project.name)


@click.command()
@click.argument("task_ref", nargs=-1, required=True)
@click.pass_context
def done(ctx: click.Context, task_ref: tuple[str, ...]) -> None:
    """Complete a task. Accepts row number, content match, or task ID.

    Examples: td done 1 | td done buy milk | td done 8bx9a0c2
    """
    api = get_client()
    fmt = _get_formatter(ctx)
    task_id = _resolve_task(" ".join(task_ref), api)

    complete_task(api, task_id)
    fmt.success(f"Completed task {task_id}", {"task_id": task_id})


@click.command()
@click.argument("task_ref", nargs=-1, required=True)
@click.pass_context
def undo(ctx: click.Context, task_ref: tuple[str, ...]) -> None:
    """Reopen a completed task. Accepts row number, content match, or task ID.

    Examples: td undo 1 | td undo buy milk | td undo 8bx9a0c2
    """
    api = get_client()
    fmt = _get_formatter(ctx)
    task_id = _resolve_task(" ".join(task_ref), api)

    uncomplete_task(api, task_id)
    fmt.success(f"Reopened task {task_id}", {"task_id": task_id})


@click.command()
@click.argument("task_ref", nargs=-1, required=True)
@click.option("--content", help="New content.")
@click.option(
    "--priority",
    type=click.IntRange(1, 4),
    help="Priority: 1=urgent, 2=high, 3=medium, 4=low.",
)
@click.option("-d", "--due", help="New due date.")
@click.option("-l", "--label", "labels", multiple=True, help="Labels (repeatable).")
@click.option("--desc", "description", help="New description.")
@click.pass_context
def edit(
    ctx: click.Context,
    task_ref: tuple[str, ...],
    content: str | None,
    priority: int | None,
    due: str | None,
    labels: tuple[str, ...],
    description: str | None,
) -> None:
    """Update a task. Accepts row number, content match, or task ID.

    Examples: td edit 1 --due friday | td edit buy milk --priority 1
    """
    api = get_client()
    fmt = _get_formatter(ctx)
    task_id = _resolve_task(" ".join(task_ref), api)

    # No flags provided — show current task values
    has_updates = content or priority or due or labels or description
    if not has_updates:
        task = api.get_task(task_id)
        fmt.task(task)
        return

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
@click.argument("task_ref", nargs=-1, required=True)
@click.option("-y", "--yes", is_flag=True, help="Skip confirmation.")
@click.pass_context
def delete(ctx: click.Context, task_ref: tuple[str, ...], yes: bool) -> None:
    """Delete a task. Accepts row number, content match, or task ID.

    Examples: td delete 1 -y | td delete buy milk -y
    """
    api = get_client()
    fmt = _get_formatter(ctx)
    task_id = _resolve_task(" ".join(task_ref), api)
    if not yes:
        if not sys.stdout.isatty():
            raise TdValidationError(
                "Cannot confirm deletion in non-interactive mode.",
                suggestion="Use --yes flag to skip confirmation.",
            )
        if not click.confirm(f"Delete task {task_id}?"):
            click.echo("Aborted.")
            return
    remove_task(api, task_id)
    fmt.success(f"Deleted task {task_id}", {"task_id": task_id})


@click.command()
@click.argument("text", nargs=-1)
@click.pass_context
def quick(ctx: click.Context, text: tuple[str, ...]) -> None:
    """Natural language task creation. Reads from stdin if no args.

    Example: td quick "Buy milk tomorrow p1 #Errands"
    """
    api = get_client()
    fmt = _get_formatter(ctx)

    content = " ".join(text) if text else (_read_stdin() or "")
    if not content:
        raise TdValidationError(
            "No task text provided.",
            suggestion="Provide text as an argument or pipe via stdin.",
        )

    task = quick_add(api, content)
    fmt.item_created("task", task)


@click.command()
@click.argument("text", nargs=-1, required=True)
@click.pass_context
def capture(ctx: click.Context, text: tuple[str, ...]) -> None:
    """Quick-capture to inbox — no parsing, no flags, minimal output.

    Example: td capture call dentist about appointment
    """
    api = get_client()
    fmt = _get_formatter(ctx)

    task, _ = create_task(api, " ".join(text))
    fmt.success(f"Captured: {task.content}", {"task_id": task.id})


@click.command()
@click.argument("query", nargs=-1, required=True)
@click.option("-p", "--project", "project_name", help="Scope to a project.")
@click.pass_context
def search(ctx: click.Context, query: tuple[str, ...], project_name: str | None) -> None:
    """Search tasks by keyword across all projects.

    Example: td search deploy | td search "blog post" -p Work
    """
    api = get_client()
    fmt = _get_formatter(ctx)

    search_term = " ".join(query)
    tasks = list_tasks(api, filter_query=f"search: {search_term}")

    if project_name:
        project_id = resolve_project(api, project_name).id
        tasks = [t for t in tasks if t.project_id == project_id]

    # Sort by relevance: exact match > starts-with > contains
    lower = search_term.lower()

    def relevance(t: object) -> int:
        content = getattr(t, "content", "").lower()
        if content == lower:
            return 0
        if content.startswith(lower):
            return 1
        return 2

    tasks.sort(key=relevance)
    fmt.task_list(tasks)
