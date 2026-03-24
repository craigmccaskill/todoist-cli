"""Output formatting engine — Rich, JSON, and Plain modes."""

from __future__ import annotations

import json
import sys
from enum import Enum
from typing import Any

import click
from rich.console import Console
from rich.table import Table
from rich.text import Text
from todoist_api_python.models import Label, Project, Section, Task

from td.core.cache import save_result_cache


class OutputMode(Enum):
    RICH = "rich"
    JSON = "json"
    PLAIN = "plain"


_FORMAT_MAP = {
    "json": OutputMode.JSON,
    "plain": OutputMode.PLAIN,
    "rich": OutputMode.RICH,
}


def resolve_output_mode(
    output_json: bool,
    plain: bool,
    color: bool = True,
    default_format: str | None = None,
) -> OutputMode:
    """Determine output mode from flags, config, and TTY detection.

    Resolution order (most specific wins):
    1. --json / --plain flags
    2. default_format (from TD_FORMAT env or config.toml)
    3. NO_COLOR / color setting
    4. TTY detection
    """
    if output_json:
        return OutputMode.JSON
    if plain:
        return OutputMode.PLAIN
    if default_format and default_format.lower() in _FORMAT_MAP:
        return _FORMAT_MAP[default_format.lower()]
    if not color:
        return OutputMode.PLAIN
    if not sys.stdout.isatty():
        return OutputMode.JSON
    return OutputMode.RICH


# Priority display config
_PRIORITY_STYLES = {
    4: ("p1", "red bold"),
    3: ("p2", "yellow"),
    2: ("p3", "blue"),
    1: ("p4", "dim"),
}


def _task_to_dict(task: Task) -> dict[str, Any]:
    """Convert a Task to a plain dict for JSON output."""
    return task.to_dict()


def _task_plain_row(task: Task) -> str:
    """Format a task as a tab-separated plain row."""
    due = task.due.date if task.due else ""
    priority = f"p{5 - task.priority}" if task.priority else ""
    labels = ",".join(task.labels) if task.labels else ""
    return f"{task.id}\t{task.content}\t{due}\t{priority}\t{labels}"


class OutputFormatter:
    """Central output formatter. Every command uses this."""

    def __init__(self, mode: OutputMode) -> None:
        self.mode = mode
        self._console = Console(stderr=False) if mode == OutputMode.RICH else None

    # --- JSON helpers ---

    def _json_out(
        self,
        data: Any,
        result_type: str,
        ok: bool = True,
    ) -> None:
        envelope: dict[str, Any] = {"ok": ok, "type": result_type, "data": data}
        click.echo(json.dumps(envelope, indent=2, default=str))

    # --- Tasks ---

    def task(self, task: Task) -> None:
        """Render a single task."""
        if self.mode == OutputMode.JSON:
            self._json_out(_task_to_dict(task), "task")
        elif self.mode == OutputMode.PLAIN:
            click.echo(_task_plain_row(task))
        else:
            self._rich_task(task)

    def task_list(self, tasks: list[Task], title: str | None = None) -> None:
        """Render a list of tasks and cache IDs for numbered references."""
        # Cache task IDs for numbered references (td done 1, etc.)
        save_result_cache([t.id for t in tasks])

        if self.mode == OutputMode.JSON:
            self._json_out([_task_to_dict(t) for t in tasks], "task_list")
        elif self.mode == OutputMode.PLAIN:
            click.echo("#\tID\tCONTENT\tDUE\tPRIORITY\tLABELS")
            for i, t in enumerate(tasks, 1):
                click.echo(f"{i}\t{_task_plain_row(t)}")
        else:
            self._rich_task_table(tasks, title)

    def _rich_task(self, task: Task) -> None:
        assert self._console is not None
        text = Text()
        p_label, p_style = _PRIORITY_STYLES.get(task.priority, ("p4", "dim"))
        text.append(f"[{p_label}] ", style=p_style)
        text.append(task.content, style="bold")
        if task.due:
            text.append(f"  {task.due.string}", style="yellow")
        if task.labels:
            for label in task.labels:
                text.append(f" @{label}", style="cyan")
        text.append(f"  ({task.id})", style="dim")
        self._console.print(text)

    def _rich_task_table(self, tasks: list[Task], title: str | None = None) -> None:
        assert self._console is not None
        table = Table(title=title or "Tasks", show_lines=False)
        table.add_column("#", style="dim", width=3)
        table.add_column("Pri", style="dim", width=3)
        table.add_column("Content", style="bold")
        table.add_column("Due", style="yellow")
        table.add_column("Labels", style="cyan")
        table.add_column("ID", style="dim")

        for i, task in enumerate(tasks, 1):
            p_label, p_style = _PRIORITY_STYLES.get(task.priority, ("p4", "dim"))
            due = task.due.string if task.due else ""
            labels = ", ".join(f"@{lbl}" for lbl in task.labels) if task.labels else ""
            table.add_row(
                str(i),
                Text(p_label, style=p_style),
                task.content,
                due,
                labels,
                task.id,
            )

        self._console.print(table)

    # --- Projects ---

    def project_list(self, projects: list[Project]) -> None:
        """Render a list of projects."""
        if self.mode == OutputMode.JSON:
            self._json_out([p.to_dict() for p in projects], "project_list")
        elif self.mode == OutputMode.PLAIN:
            click.echo("ID\tNAME")
            for p in projects:
                click.echo(f"{p.id}\t{p.name}")
        else:
            self._rich_project_table(projects)

    def _rich_project_table(self, projects: list[Project]) -> None:
        assert self._console is not None
        table = Table(title="Projects")
        table.add_column("Name", style="bold")
        table.add_column("ID", style="dim")
        table.add_column("", width=3)

        for p in projects:
            fav = "*" if p.is_favorite else ""
            table.add_row(p.name, p.id, fav)

        self._console.print(table)

    # --- Sections ---

    def section_list(self, sections: list[Section]) -> None:
        """Render a list of sections."""
        if self.mode == OutputMode.JSON:
            self._json_out([s.to_dict() for s in sections], "section_list")
        elif self.mode == OutputMode.PLAIN:
            click.echo("ID\tNAME")
            for s in sections:
                click.echo(f"{s.id}\t{s.name}")
        else:
            self._rich_section_table(sections)

    def _rich_section_table(self, sections: list[Section]) -> None:
        assert self._console is not None
        table = Table(title="Sections")
        table.add_column("Name", style="bold")
        table.add_column("ID", style="dim")

        for s in sections:
            table.add_row(s.name, s.id)

        self._console.print(table)

    # --- Labels ---

    def label_list(self, labels: list[Label]) -> None:
        """Render a list of labels."""
        if self.mode == OutputMode.JSON:
            self._json_out([lbl.to_dict() for lbl in labels], "label_list")
        elif self.mode == OutputMode.PLAIN:
            click.echo("ID\tNAME")
            for lbl in labels:
                click.echo(f"{lbl.id}\t{lbl.name}")
        else:
            self._rich_label_table(labels)

    def _rich_label_table(self, labels: list[Label]) -> None:
        assert self._console is not None
        table = Table(title="Labels")
        table.add_column("Name", style="bold")
        table.add_column("ID", style="dim")

        for lbl in labels:
            table.add_row(f"@{lbl.name}", lbl.id)

        self._console.print(table)

    # --- Generic ---

    def success(self, message: str, data: dict[str, Any] | None = None) -> None:
        """Render a success message."""
        if self.mode == OutputMode.JSON:
            self._json_out(data or {}, "success")
        elif self.mode == OutputMode.PLAIN:
            click.echo(message)
        else:
            assert self._console is not None
            self._console.print(f"[green]{message}[/green]")

    def item_created(
        self,
        item_type: str,
        item: Task | Project | Label | Section,
        created: bool = True,
    ) -> None:
        """Render confirmation of item creation."""
        item_dict = item.to_dict()
        if self.mode == OutputMode.JSON:
            self._json_out(
                {**item_dict, "created": created},
                f"{item_type}_created",
            )
        elif self.mode == OutputMode.PLAIN:
            action = "Created" if created else "Already exists"
            click.echo(f"{action}\t{item_dict.get('id', '')}")
        else:
            assert self._console is not None
            name = item_dict.get("content", item_dict.get("name", ""))
            item_id = item_dict.get("id", "")
            if created:
                self._console.print(
                    f"[green]Created {item_type}:[/green] {name} [dim]({item_id})[/dim]"
                )
            else:
                self._console.print(
                    f"[yellow]Already exists:[/yellow] {name} [dim]({item_id})[/dim]"
                )
