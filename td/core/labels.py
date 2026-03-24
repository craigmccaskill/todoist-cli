"""Label resolution."""

from __future__ import annotations

from todoist_api_python.api import TodoistAPI
from todoist_api_python.models import Label

from td.cli.errors import LABEL_NOT_FOUND, TdError


def _collect_labels(api: TodoistAPI) -> list[Label]:
    """Fetch all labels."""
    return [lbl for page in api.get_labels() for lbl in page]


def resolve_label(api: TodoistAPI, name_or_id: str) -> Label:
    """Resolve a label by name (case-insensitive) or ID."""
    labels = _collect_labels(api)

    for lbl in labels:
        if lbl.id == name_or_id:
            return lbl

    lower = name_or_id.lower()
    for lbl in labels:
        if lbl.name.lower() == lower:
            return lbl

    raise TdError(
        f"Label '{name_or_id}' not found",
        code=LABEL_NOT_FOUND,
        suggestion="Run `td labels` to list available labels.",
    )
