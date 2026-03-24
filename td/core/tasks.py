"""Task business logic — no CLI dependency."""

from __future__ import annotations

from collections.abc import Iterator

from todoist_api_python.api import TodoistAPI
from todoist_api_python.models import Task


def _collect(iterator: Iterator[list[Task]]) -> list[Task]:
    """Flatten a paginated iterator into a flat list."""
    return [item for page in iterator for item in page]


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

    kwargs: dict[str, object] = {}
    if project_id:
        kwargs["project_id"] = project_id
    if section_id:
        kwargs["section_id"] = section_id
    if priority:
        kwargs["priority"] = priority
    if due_string:
        kwargs["due_string"] = due_string
    if labels:
        kwargs["labels"] = labels
    if description:
        kwargs["description"] = description

    task = api.add_task(content, **kwargs)  # type: ignore[arg-type]
    return task, True


def _find_duplicate(
    api: TodoistAPI,
    content: str,
    *,
    project_id: str | None = None,
) -> Task | None:
    """Check if a task with the same content exists."""
    kwargs: dict[str, object] = {}
    if project_id:
        kwargs["project_id"] = project_id
    tasks = _collect(api.get_tasks(**kwargs))  # type: ignore[arg-type]
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

    kwargs: dict[str, object] = {}
    if project_id:
        kwargs["project_id"] = project_id
    if label:
        kwargs["label"] = label
    return _collect(api.get_tasks(**kwargs))  # type: ignore[arg-type]


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
    kwargs: dict[str, object] = {}
    if content is not None:
        kwargs["content"] = content
    if priority is not None:
        kwargs["priority"] = priority
    if due_string is not None:
        kwargs["due_string"] = due_string
    if labels is not None:
        kwargs["labels"] = labels
    if description is not None:
        kwargs["description"] = description

    return api.update_task(task_id, **kwargs)  # type: ignore[arg-type]


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
