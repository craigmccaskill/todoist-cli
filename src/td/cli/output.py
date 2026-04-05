"""Output formatting engine — Rich, JSON, and Plain modes."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from enum import Enum
from typing import Any

import click
from rich.console import Console
from rich.table import Table
from rich.text import Text
from todoist_api_python.models import Comment, Label, Project, Section, Task

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


def _is_overdue(due_string: str) -> bool:
    """Check if a YYYY-MM-DD date string is before today."""
    try:
        due_date = datetime.strptime(due_string, "%Y-%m-%d").replace(tzinfo=timezone.utc)
        today = datetime.now(tz=timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
        return due_date < today
    except ValueError:
        return False


def _format_timestamp(iso_str: str) -> str:
    """Format an ISO timestamp into a human-readable relative string.

    <1h -> "Xm ago", <24h -> "Xh ago", <7d -> "Xd ago", else "Mon DD".
    """
    try:
        posted = datetime.fromisoformat(str(iso_str))
        if posted.tzinfo is None:
            posted = posted.replace(tzinfo=timezone.utc)
        now = datetime.now(tz=timezone.utc)
        delta = now - posted
        total_seconds = int(delta.total_seconds())

        if total_seconds < 0:
            return str(iso_str)
        if total_seconds < 3600:
            minutes = max(1, total_seconds // 60)
            return f"{minutes}m ago"
        if total_seconds < 86400:
            hours = total_seconds // 3600
            return f"{hours}h ago"
        if total_seconds < 604800:
            days = total_seconds // 86400
            return f"{days}d ago"
        return posted.strftime("%b %d")
    except (ValueError, TypeError):
        return str(iso_str)


def _empty_message(item_type: str) -> str:
    """Return a user-friendly empty state message."""
    messages = {
        "tasks": "No tasks found.",
        "projects": "No projects found.",
        "labels": "No labels found.",
        "sections": "No sections found.",
        "comments": "No comments found.",
    }
    return messages.get(item_type, f"No {item_type} found.")


def _task_to_dict(task: Task, project_names: dict[str, str] | None = None) -> dict[str, Any]:
    """Convert a Task to a plain dict for JSON output."""
    d = task.to_dict()
    if project_names and task.project_id:
        d["project_name"] = project_names.get(task.project_id, "")
    return d


def _task_plain_row(
    task: Task,
    project_names: dict[str, str] | None = None,
    *,
    show_project: bool = True,
    show_labels: bool = True,
) -> str:
    """Format a task as a tab-separated plain row.

    Column order matches Rich: PRI, CONTENT, PROJECT, DUE, LABELS.
    """
    due = str(task.due.date) if task.due else ""
    priority = f"p{5 - task.priority}" if task.priority else ""
    parts = [priority, task.content]
    if show_project:
        project = project_names.get(task.project_id, "") if project_names else ""
        parts.append(project)
    parts.append(due)
    if show_labels:
        labels = ",".join(task.labels) if task.labels else ""
        parts.append(labels)
    return "\t".join(parts)


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

    def task_detail(self, task: Task, project_name: str | None = None) -> None:
        """Render full task details."""
        if self.mode == OutputMode.JSON:
            d = _task_to_dict(task)
            if project_name:
                d["project_name"] = project_name
            self._json_out(d, "task")
        elif self.mode == OutputMode.PLAIN:
            click.echo(f"ID\t{task.id}")
            click.echo(f"Content\t{task.content}")
            if task.description:
                click.echo(f"Description\t{task.description}")
            if project_name:
                click.echo(f"Project\t{project_name}")
            p_label = f"p{5 - task.priority}" if task.priority else ""
            click.echo(f"Priority\t{p_label}")
            click.echo(f"Due\t{task.due.string if task.due else ''}")
            if task.labels:
                click.echo(f"Labels\t{', '.join(task.labels)}")
        else:
            self._rich_task_detail(task, project_name)

    def _rich_task_detail(self, task: Task, project_name: str | None = None) -> None:
        assert self._console is not None
        from rich.panel import Panel

        p_label, p_style = _PRIORITY_STYLES.get(task.priority, ("p4", "dim"))
        lines: list[str] = []
        if project_name:
            lines.append(f"[dim]Project:[/dim]  {project_name}")
        lines.append(f"[dim]Priority:[/dim] [{p_style}]{p_label}[/{p_style}]")
        if task.due:
            due_style = "red" if _is_overdue(str(task.due.date)) else "yellow"
            lines.append(f"[dim]Due:[/dim]      [{due_style}]{task.due.string}[/{due_style}]")
        if task.labels:
            lbl_str = ", ".join(f"[cyan]@{lbl}[/cyan]" for lbl in task.labels)
            lines.append(f"[dim]Labels:[/dim]   {lbl_str}")
        if task.description:
            lines.append(f"\n{task.description}")
        lines.append(f"\n[dim]ID: {task.id}[/dim]")

        self._console.print(
            Panel(
                "\n".join(lines),
                title=f"[bold]{task.content}[/bold]",
                expand=False,
            )
        )

    def task_list(
        self,
        tasks: list[Task],
        title: str | None = None,
        project_names: dict[str, str] | None = None,
        show_project: bool | None = None,
        show_labels: bool | None = None,
    ) -> None:
        """Render a list of tasks and cache IDs for numbered references."""
        # Cache task IDs for numbered references (td done 1, etc.)
        save_result_cache([t.id for t in tasks])

        if not tasks:
            if self.mode == OutputMode.JSON:
                self._json_out([], "task_list")
            elif self.mode == OutputMode.PLAIN:
                click.echo(_empty_message("tasks"))
            else:
                assert self._console is not None
                self._console.print(f"[dim]{_empty_message('tasks')}[/dim]")
            return

        # Smart column visibility (same logic for Rich and Plain)
        has_labels = any(t.labels for t in tasks) if show_labels is None else show_labels
        has_project = project_names is not None if show_project is None else show_project

        if self.mode == OutputMode.JSON:
            self._json_out([_task_to_dict(t, project_names) for t in tasks], "task_list")
        elif self.mode == OutputMode.PLAIN:
            header_parts = ["#", "PRI", "CONTENT"]
            if has_project:
                header_parts.append("PROJECT")
            header_parts.append("DUE")
            if has_labels:
                header_parts.append("LABELS")
            click.echo("\t".join(header_parts))
            for i, t in enumerate(tasks, 1):
                row = _task_plain_row(
                    t,
                    project_names,
                    show_project=has_project,
                    show_labels=has_labels,
                )
                click.echo(f"{i}\t{row}")
        else:
            self._rich_task_table(
                tasks,
                title,
                project_names,
                show_labels=has_labels,
                show_project=has_project,
            )

    def _rich_task(self, task: Task) -> None:
        assert self._console is not None
        text = Text()
        p_label, p_style = _PRIORITY_STYLES.get(task.priority, ("p4", "dim"))
        text.append("\u258e ", style=p_style)
        text.append(p_label, style=p_style)
        text.append(f"  {task.content}")
        if task.due:
            due_style = "red" if _is_overdue(str(task.due.date)) else "yellow"
            text.append(f"  {task.due.string}", style=due_style)
        if task.labels:
            for label in task.labels:
                text.append(f" @{label}", style="cyan")
        self._console.print(text)

    def _rich_task_table(
        self,
        tasks: list[Task],
        title: str | None = None,
        project_names: dict[str, str] | None = None,
        show_labels: bool = False,
        show_project: bool = False,
    ) -> None:
        assert self._console is not None

        table = Table(title=title or "Tasks", show_lines=False)
        table.add_column("#", style="dim", width=3)
        table.add_column("", width=2)  # priority bar
        table.add_column("Pri", width=3)
        table.add_column("Content")
        if show_project:
            table.add_column("Project", style="dim")
        table.add_column("Due")
        if show_labels:
            table.add_column("Labels", style="cyan")

        for i, task in enumerate(tasks, 1):
            p_label, p_style = _PRIORITY_STYLES.get(task.priority, ("p4", "dim"))
            due_str = task.due.string if task.due else ""
            due_style = "red" if task.due and _is_overdue(str(task.due.date)) else "yellow"
            row: list[str | Text] = [
                str(i),
                Text("\u258e", style=p_style),
                Text(p_label, style=p_style),
                task.content,
            ]
            if show_project:
                project = project_names.get(task.project_id, "") if project_names else ""
                row.append(project)
            row.append(Text(due_str, style=due_style))
            if show_labels:
                labels = ", ".join(f"@{lbl}" for lbl in task.labels) if task.labels else ""
                row.append(labels)
            table.add_row(*row)

        self._console.print(table)

    # --- Projects ---

    def project_list(self, projects: list[Project]) -> None:
        """Render a list of projects."""
        if not projects:
            if self.mode == OutputMode.JSON:
                self._json_out([], "project_list")
            elif self.mode == OutputMode.PLAIN:
                click.echo(_empty_message("projects"))
            else:
                assert self._console is not None
                self._console.print(f"[dim]{_empty_message('projects')}[/dim]")
            return

        if self.mode == OutputMode.JSON:
            self._json_out([p.to_dict() for p in projects], "project_list")
        elif self.mode == OutputMode.PLAIN:
            click.echo("NAME\t\u2605\tID")
            for p in projects:
                fav = "*" if p.is_favorite else ""
                click.echo(f"{p.name}\t{fav}\t{p.id}")
        else:
            self._rich_project_table(projects)

    def _rich_project_table(self, projects: list[Project]) -> None:
        assert self._console is not None
        table = Table(title="Projects")
        table.add_column("Name", style="bold")
        table.add_column("\u2605", width=3)
        table.add_column("ID", style="dim")

        for p in projects:
            fav = "*" if p.is_favorite else ""
            table.add_row(p.name, fav, p.id)

        self._console.print(table)

    # --- Sections ---

    def section_list(self, sections: list[Section]) -> None:
        """Render a list of sections."""
        if not sections:
            if self.mode == OutputMode.JSON:
                self._json_out([], "section_list")
            elif self.mode == OutputMode.PLAIN:
                click.echo(_empty_message("sections"))
            else:
                assert self._console is not None
                self._console.print(f"[dim]{_empty_message('sections')}[/dim]")
            return

        if self.mode == OutputMode.JSON:
            self._json_out([s.to_dict() for s in sections], "section_list")
        elif self.mode == OutputMode.PLAIN:
            click.echo("NAME\tID")
            for s in sections:
                click.echo(f"{s.name}\t{s.id}")
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
        if not labels:
            if self.mode == OutputMode.JSON:
                self._json_out([], "label_list")
            elif self.mode == OutputMode.PLAIN:
                click.echo(_empty_message("labels"))
            else:
                assert self._console is not None
                self._console.print(f"[dim]{_empty_message('labels')}[/dim]")
            return

        if self.mode == OutputMode.JSON:
            self._json_out([lbl.to_dict() for lbl in labels], "label_list")
        elif self.mode == OutputMode.PLAIN:
            click.echo("NAME\tID")
            for lbl in labels:
                click.echo(f"@{lbl.name}\t{lbl.id}")
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

    # --- Comments ---

    def comment_list(self, comments: list[Comment]) -> None:
        """Render a list of comments."""
        if not comments:
            if self.mode == OutputMode.JSON:
                self._json_out([], "comment_list")
            elif self.mode == OutputMode.PLAIN:
                click.echo(_empty_message("comments"))
            else:
                assert self._console is not None
                self._console.print(f"[dim]{_empty_message('comments')}[/dim]")
            return

        if self.mode == OutputMode.JSON:
            self._json_out([c.to_dict() for c in comments], "comment_list")
        elif self.mode == OutputMode.PLAIN:
            click.echo("CONTENT\tPOSTED\tID")
            for c in comments:
                posted = _format_timestamp(str(c.posted_at))
                click.echo(f"{c.content}\t{posted}\t{c.id}")
        else:
            self._rich_comment_table(comments)

    def _rich_comment_table(self, comments: list[Comment]) -> None:
        assert self._console is not None
        table = Table(title="Comments", show_lines=False)
        table.add_column("Content", style="bold")
        table.add_column("Posted", style="dim")
        table.add_column("ID", style="dim")

        for c in comments:
            posted = _format_timestamp(str(c.posted_at))
            table.add_row(c.content, posted, c.id)

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
