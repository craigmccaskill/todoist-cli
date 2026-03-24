"""Section resolution."""

from __future__ import annotations

from todoist_api_python.api import TodoistAPI
from todoist_api_python.models import Section

from td.cli.errors import SECTION_NOT_FOUND, TdError


def _collect_sections(api: TodoistAPI, project_id: str | None = None) -> list[Section]:
    """Fetch sections, optionally filtered by project."""
    return [s for page in api.get_sections(project_id=project_id) for s in page]


def resolve_section(api: TodoistAPI, name_or_id: str, *, project_id: str | None = None) -> Section:
    """Resolve a section by name (case-insensitive) or ID."""
    sections = _collect_sections(api, project_id=project_id)

    for sec in sections:
        if sec.id == name_or_id:
            return sec

    lower = name_or_id.lower()
    for sec in sections:
        if sec.name.lower() == lower:
            return sec

    raise TdError(
        f"Section '{name_or_id}' not found",
        code=SECTION_NOT_FOUND,
        suggestion="Run `td sections -p <project>` to list sections.",
    )
