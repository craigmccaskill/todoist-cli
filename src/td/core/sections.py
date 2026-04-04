"""Section resolution with caching."""

from __future__ import annotations

import json
import logging

from todoist_api_python.api import TodoistAPI
from todoist_api_python.models import Section

from td.core.cache import load_name_cache, save_name_cache
from td.core.exceptions import SectionNotFoundError

logger = logging.getLogger(__name__)


def _collect_sections(api: TodoistAPI, project_id: str | None = None) -> list[Section]:
    """Fetch sections, optionally filtered by project."""
    if not project_id:
        try:
            cached = load_name_cache()
            if cached.get("sections"):
                return [Section.from_dict(s) for s in cached["sections"]]
        except (OSError, json.JSONDecodeError, KeyError):
            logger.debug("Section cache read failed", exc_info=True)

    sections = [s for page in api.get_sections(project_id=project_id) for s in page]
    if not project_id:
        try:
            save_name_cache(sections=[s.to_dict() for s in sections])
        except (OSError, json.JSONDecodeError, KeyError, TypeError):
            logger.debug("Section cache write failed", exc_info=True)
    return sections


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

    raise SectionNotFoundError(
        f"Section '{name_or_id}' not found",
        suggestion="Run `td sections -p <project>` to list sections.",
    )
