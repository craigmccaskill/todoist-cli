"""Domain-specific pickers built on the generic picker."""

from __future__ import annotations

from typing import Any

from todoist_api_python.models import Label, Project, Section, Task

from td.tui.picker import pick_from_list

# --- Priority mapping (same as cli/output.py) ---
_PRIORITY_LABELS = {4: "p1", 3: "p2", 2: "p3", 1: "p4"}


def pick_task(tasks: list[Task], title: str = "Select a task") -> str | None:
    """Show a task picker. Returns task ID or None."""
    rows: list[dict[str, Any]] = []
    for i, t in enumerate(tasks, 1):
        rows.append(
            {
                "id": t.id,
                "#": str(i),
                "Pri": _PRIORITY_LABELS.get(t.priority, "p4"),
                "Content": t.content,
                "Due": t.due.string if t.due else "",
                "Labels": ", ".join(f"@{lbl}" for lbl in t.labels) if t.labels else "",
            }
        )
    return pick_from_list(
        title,
        columns=["#", "Pri", "Content", "Due", "Labels"],
        rows=rows,
    )


def pick_project(projects: list[Project], title: str = "Select a project") -> str | None:
    """Show a project picker. Returns project ID or None."""
    rows: list[dict[str, Any]] = []
    for p in projects:
        fav = "★" if p.is_favorite else ""
        rows.append({"id": p.id, "Name": p.name, " ": fav})
    return pick_from_list(title, columns=["Name", " "], rows=rows)


def pick_label(labels: list[Label], title: str = "Select a label") -> str | None:
    """Show a label picker. Returns label name or None."""
    rows: list[dict[str, Any]] = []
    for lbl in labels:
        rows.append({"id": lbl.name, "Name": f"@{lbl.name}"})
    return pick_from_list(title, columns=["Name"], rows=rows)


def pick_section(sections: list[Section], title: str = "Select a section") -> str | None:
    """Show a section picker. Returns section ID or None."""
    rows: list[dict[str, Any]] = []
    for s in sections:
        rows.append({"id": s.id, "Name": s.name})
    return pick_from_list(title, columns=["Name"], rows=rows)


def pick_priority(title: str = "Select priority") -> int | None:
    """Show a priority picker. Returns API priority value (4=urgent) or None."""
    rows = [
        {"id": "4", "Priority": "p1 — Urgent"},
        {"id": "3", "Priority": "p2 — High"},
        {"id": "2", "Priority": "p3 — Medium"},
        {"id": "1", "Priority": "p4 — Low"},
    ]
    result = pick_from_list(title, columns=["Priority"], rows=rows)
    return int(result) if result else None
