"""Project resolution — name to ID mapping with caching."""

from __future__ import annotations

import json
import logging

from todoist_api_python.api import TodoistAPI
from todoist_api_python.models import Project

from td.core.cache import load_name_cache, save_name_cache
from td.core.exceptions import ProjectNotFoundError

logger = logging.getLogger(__name__)


def _collect_projects(api: TodoistAPI, use_cache: bool = True) -> list[Project]:
    """Fetch all projects, using cache if available."""
    if use_cache:
        try:
            cached = load_name_cache()
            if cached.get("projects"):
                return [Project.from_dict(p) for p in cached["projects"]]
        except (OSError, json.JSONDecodeError, KeyError):
            logger.debug("Project cache read failed", exc_info=True)

    projects = [p for page in api.get_projects() for p in page]
    try:
        save_name_cache(projects=[p.to_dict() for p in projects])
    except (OSError, json.JSONDecodeError, KeyError, TypeError):
        logger.debug("Project cache write failed", exc_info=True)
    return projects


def resolve_project(api: TodoistAPI, name_or_id: str) -> Project:
    """Resolve a project by name (case-insensitive) or ID.

    Raises ProjectNotFoundError with suggestions if not found.
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

    raise ProjectNotFoundError(
        f"Project '{name_or_id}' not found",
        suggestion=suggestion,
        details={"query": name_or_id},
    )


def create_project(
    api: TodoistAPI,
    name: str,
    *,
    parent_id: str | None = None,
    is_favorite: bool = False,
) -> Project:
    """Create a new project."""
    return api.add_project(
        name,
        parent_id=parent_id,
        is_favorite=is_favorite or None,
    )


def get_project_name_map(api: TodoistAPI) -> dict[str, str]:
    """Return {project_id: project_name} from cache or API."""
    projects = _collect_projects(api)
    return {p.id: p.name for p in projects}


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
    raise ProjectNotFoundError("Could not find Inbox project")
