"""Task business logic — no CLI dependency."""

from __future__ import annotations

from collections.abc import Callable, Iterator
from typing import Any

from todoist_api_python.api import TodoistAPI
from todoist_api_python.models import Task

SORT_OPTIONS = ("priority", "due", "project", "created")


def _collect(iterator: Iterator[list[Task]]) -> list[Task]:
    """Flatten a paginated iterator into a flat list."""
    return [item for page in iterator for item in page]


def _due_sort_value(task: Task) -> tuple[int, str]:
    """Sort key for due dates. No date sorts last."""
    if task.due is None:
        return (1, "9999-99-99")
    return (0, str(task.due.date) if task.due.date else "9999-99-99")


def _key_priority(t: Task) -> Any:
    return (-t.priority, _due_sort_value(t))


def _key_due(t: Task) -> Any:
    return (_due_sort_value(t), -t.priority)


def _key_project(t: Task) -> Any:
    return (t.project_id or "", -t.priority)


def _key_created(t: Task) -> Any:
    return t.id


_SORT_KEYS: dict[str, Callable[[Task], Any]] = {
    "priority": _key_priority,
    "due": _key_due,
    "project": _key_project,
    "created": _key_created,
}


def sort_tasks(
    tasks: list[Task],
    sort_by: str = "priority",
    reverse: bool = False,
) -> list[Task]:
    """Sort tasks by the given key.

    priority: urgent (API 4) first → low (API 1) last
    due: overdue → today → future → no date
    project: alphabetical by project_id
    created: newest first
    """
    key = _SORT_KEYS.get(sort_by, _key_priority)
    return sorted(tasks, key=key, reverse=reverse)


def find_task_by_content(
    api: TodoistAPI,
    query: str,
) -> list[Task]:
    """Find tasks whose content matches a query (case-insensitive substring).

    Returns all matching tasks, sorted by relevance (exact > starts-with > contains).
    """
    tasks = _collect(api.get_tasks())
    lower = query.lower()

    exact = [t for t in tasks if t.content.lower() == lower]
    if exact:
        return exact

    starts = [t for t in tasks if t.content.lower().startswith(lower)]
    if starts:
        return starts

    contains = [t for t in tasks if lower in t.content.lower()]
    return contains


def create_task(
    api: TodoistAPI,
    content: str,
    *,
    project_id: str | None = None,
    priority: int | None = None,
    due_string: str | None = None,
    labels: list[str] | None = None,
    description: str | None = None,
    section_id: str | None = None,
    idempotent: bool = False,
) -> tuple[Task, bool]:
    """Create a task. Returns (task, created).

    If idempotent=True, checks for existing matching task first.
    """
    if idempotent:
        existing = _find_duplicate(api, content, project_id=project_id)
        if existing:
            return existing, False

    task = api.add_task(
        content,
        project_id=project_id,
        section_id=section_id,
        priority=priority,
        due_string=due_string,
        labels=labels,
        description=description,
    )
    return task, True


def _find_duplicate(
    api: TodoistAPI,
    content: str,
    *,
    project_id: str | None = None,
) -> Task | None:
    """Check if a task with the same content exists."""
    tasks = _collect(api.get_tasks(project_id=project_id))
    for task in tasks:
        if task.content.strip().lower() == content.strip().lower():
            return task
    return None


def list_tasks(
    api: TodoistAPI,
    *,
    project_id: str | None = None,
    label: str | None = None,
    filter_query: str | None = None,
) -> list[Task]:
    """List tasks with optional filters."""
    if filter_query:
        return _collect(api.filter_tasks(query=filter_query))

    return _collect(api.get_tasks(project_id=project_id, label=label))


def complete_task(api: TodoistAPI, task_id: str) -> bool:
    """Mark a task as complete."""
    api.complete_task(task_id)
    return True


def edit_task(
    api: TodoistAPI,
    task_id: str,
    *,
    content: str | None = None,
    priority: int | None = None,
    due_string: str | None = None,
    labels: list[str] | None = None,
    description: str | None = None,
) -> Task:
    """Update task fields."""
    return api.update_task(
        task_id,
        content=content,
        priority=priority,
        due_string=due_string,
        labels=labels,
        description=description,
    )


def remove_task(api: TodoistAPI, task_id: str) -> bool:
    """Delete a task."""
    api.delete_task(task_id)
    return True


def uncomplete_task(api: TodoistAPI, task_id: str) -> bool:
    """Reopen a completed task."""
    api.uncomplete_task(task_id)
    return True


def quick_add(api: TodoistAPI, text: str) -> Task:
    """Natural language task creation via Todoist's quick-add."""
    return api.add_task_quick(text)
