"""Label resolution with caching."""

from __future__ import annotations

import json
import logging

from todoist_api_python.api import TodoistAPI
from todoist_api_python.models import Label

from td.cli.errors import LABEL_NOT_FOUND, TdError
from td.core.cache import load_name_cache, save_name_cache

logger = logging.getLogger(__name__)


def _collect_labels(api: TodoistAPI, use_cache: bool = True) -> list[Label]:
    """Fetch all labels, using cache if available."""
    if use_cache:
        try:
            cached = load_name_cache()
            if cached.get("labels"):
                return [Label.from_dict(lbl) for lbl in cached["labels"]]
        except (OSError, json.JSONDecodeError, KeyError):
            logger.debug("Label cache read failed", exc_info=True)

    labels = [lbl for page in api.get_labels() for lbl in page]
    try:
        save_name_cache(labels=[lbl.to_dict() for lbl in labels])
    except (OSError, json.JSONDecodeError, KeyError):
        logger.debug("Label cache write failed", exc_info=True)
    return labels


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
