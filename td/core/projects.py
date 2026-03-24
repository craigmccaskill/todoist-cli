"""Project resolution — name to ID mapping."""

from __future__ import annotations

from todoist_api_python.api import TodoistAPI
from todoist_api_python.models import Project

from td.cli.errors import TdProjectNotFoundError


def _collect_projects(api: TodoistAPI) -> list[Project]:
    """Fetch all projects."""
    return [p for page in api.get_projects() for p in page]


def resolve_project(api: TodoistAPI, name_or_id: str) -> Project:
    """Resolve a project by name (case-insensitive) or ID.

    Raises TdProjectNotFoundError with suggestions if not found.
    """
    projects = _collect_projects(api)

    # Try exact ID match first
    for proj in projects:
        if proj.id == name_or_id:
            return proj

    # Try case-insensitive name match
    lower = name_or_id.lower()
    for proj in projects:
        if proj.name.lower() == lower:
            return proj

    # Try substring match for suggestions
    partial = [p.name for p in projects if lower in p.name.lower()]
    suggestion = "Run `td projects` to list available projects."
    if partial:
        suggestion += f" Did you mean: {', '.join(partial[:3])}?"

    raise TdProjectNotFoundError(
        f"Project '{name_or_id}' not found",
        suggestion=suggestion,
        details={"query": name_or_id},
    )


def get_inbox_project(api: TodoistAPI) -> Project:
    """Find the Inbox project."""
    projects = _collect_projects(api)
    for proj in projects:
        if proj.is_inbox_project:
            return proj
    # Fallback: look by name
    for proj in projects:
        if proj.name.lower() == "inbox":
            return proj
    raise TdProjectNotFoundError("Could not find Inbox project")
