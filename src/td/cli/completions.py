"""Dynamic shell completions for project, label, and section names."""

from __future__ import annotations

import contextlib
from typing import TYPE_CHECKING

from click.shell_completion import CompletionItem

if TYPE_CHECKING:
    import click


def _complete_projects(
    ctx: click.Context, param: click.Parameter, incomplete: str
) -> list[CompletionItem]:
    """Complete project names from cache or API."""
    names = _get_cached_project_names()
    return [CompletionItem(name) for name in names if name.lower().startswith(incomplete.lower())]


def _complete_labels(
    ctx: click.Context, param: click.Parameter, incomplete: str
) -> list[CompletionItem]:
    """Complete label names from cache or API."""
    names = _get_cached_label_names()
    return [CompletionItem(name) for name in names if name.lower().startswith(incomplete.lower())]


def _complete_sections(
    ctx: click.Context, param: click.Parameter, incomplete: str
) -> list[CompletionItem]:
    """Complete section names from cache or API."""
    names = _get_cached_section_names()
    return [CompletionItem(name) for name in names if name.lower().startswith(incomplete.lower())]


def _get_cached_project_names() -> list[str]:
    """Get project names from the name cache, falling back to API."""
    with contextlib.suppress(Exception):
        from td.core.cache import load_name_cache

        cached = load_name_cache()
        if cached.get("projects"):
            return [p["name"] for p in cached["projects"]]

    # Try API as fallback
    with contextlib.suppress(Exception):
        from td.core.client import get_client
        from td.core.projects import _collect_projects

        api = get_client()
        projects = _collect_projects(api)
        return [p.name for p in projects]

    return []


def _get_cached_label_names() -> list[str]:
    """Get label names from the name cache, falling back to API."""
    with contextlib.suppress(Exception):
        from td.core.cache import load_name_cache

        cached = load_name_cache()
        if cached.get("labels"):
            return [lbl["name"] for lbl in cached["labels"]]

    with contextlib.suppress(Exception):
        from td.core.client import get_client
        from td.core.labels import _collect_labels

        api = get_client()
        labels = _collect_labels(api)
        return [lbl.name for lbl in labels]

    return []


def _get_cached_section_names() -> list[str]:
    """Get section names from the name cache, falling back to API."""
    with contextlib.suppress(Exception):
        from td.core.cache import load_name_cache

        cached = load_name_cache()
        if cached.get("sections"):
            return [s["name"] for s in cached["sections"]]

    return []
