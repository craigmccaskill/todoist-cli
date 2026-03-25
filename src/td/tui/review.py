"""Review mode TUI — interactive inbox processing."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, ClassVar

from textual import on
from textual.app import App, ComposeResult
from textual.binding import Binding, BindingType
from textual.containers import Vertical
from textual.screen import ModalScreen
from textual.widgets import DataTable, Input, Static
from todoist_api_python.api import TodoistAPI
from todoist_api_python.models import Task

# --- Priority mapping ---
_PRIORITY_LABELS = {4: "p1", 3: "p2", 2: "p3", 1: "p4"}
_PRIORITY_STYLES = {4: "red bold", 3: "yellow", 2: "blue", 1: "dim"}


@dataclass
class ReviewStats:
    """Track changes made during the review session."""

    updated: list[str] = field(default_factory=list)
    completed: list[str] = field(default_factory=list)
    skipped: int = 0
    undo_stack: list[dict[str, Any]] = field(default_factory=list)


class ProjectPickerScreen(ModalScreen[str | None]):
    """Modal screen for picking a project."""

    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("escape", "cancel", "Cancel"),
    ]

    def __init__(self, projects: list[dict[str, str]]) -> None:
        super().__init__()
        self._projects = projects

    def compose(self) -> ComposeResult:
        yield Static("Set project:", id="picker-title")
        table: DataTable[str] = DataTable(cursor_type="row", id="picker-table")
        table.add_column("Name", key="name")
        for p in self._projects:
            table.add_row(p["name"], key=p["id"])
        yield table

    @on(DataTable.RowSelected)
    def on_row_selected(self, event: DataTable.RowSelected) -> None:
        self.dismiss(str(event.row_key.value))

    def action_cancel(self) -> None:
        self.dismiss(None)


class PriorityPickerScreen(ModalScreen[int | None]):
    """Modal screen for picking a priority."""

    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("escape", "cancel", "Cancel"),
    ]

    def compose(self) -> ComposeResult:
        yield Static("Set priority:", id="picker-title")
        table: DataTable[str] = DataTable(cursor_type="row", id="picker-table")
        table.add_column("Priority", key="priority")
        table.add_row("p1 — Urgent", key="4")
        table.add_row("p2 — High", key="3")
        table.add_row("p3 — Medium", key="2")
        table.add_row("p4 — Low", key="1")
        yield table

    @on(DataTable.RowSelected)
    def on_row_selected(self, event: DataTable.RowSelected) -> None:
        self.dismiss(int(str(event.row_key.value)))

    def action_cancel(self) -> None:
        self.dismiss(None)


class LabelPickerScreen(ModalScreen[str | None]):
    """Modal screen for picking a label."""

    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("escape", "cancel", "Cancel"),
    ]

    def __init__(self, labels: list[str]) -> None:
        super().__init__()
        self._labels = labels

    def compose(self) -> ComposeResult:
        yield Static("Add label:", id="picker-title")
        table: DataTable[str] = DataTable(cursor_type="row", id="picker-table")
        table.add_column("Label", key="label")
        for lbl in self._labels:
            table.add_row(f"@{lbl}", key=lbl)
        yield table

    @on(DataTable.RowSelected)
    def on_row_selected(self, event: DataTable.RowSelected) -> None:
        self.dismiss(str(event.row_key.value))

    def action_cancel(self) -> None:
        self.dismiss(None)


class DueDateScreen(ModalScreen[str | None]):
    """Modal screen for entering a due date."""

    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("escape", "cancel", "Cancel"),
    ]

    def __init__(self, task_content: str) -> None:
        super().__init__()
        self._task_content = task_content

    def compose(self) -> ComposeResult:
        yield Static(f'Due date for "{self._task_content}":', id="picker-title")
        yield Input(placeholder="e.g. tomorrow, next friday, 2026-04-01")

    @on(Input.Submitted)
    def on_input_submitted(self, event: Input.Submitted) -> None:
        value = event.value.strip()
        self.dismiss(value if value else None)

    def action_cancel(self) -> None:
        self.dismiss(None)


class ReviewApp(App[ReviewStats]):
    """Interactive inbox review TUI."""

    CSS = """
    Screen {
        layout: vertical;
    }
    #header {
        text-align: center;
        padding: 1 0;
        color: $text;
        text-style: bold;
    }
    #status-line {
        text-align: left;
        padding: 0 1;
        color: $text-muted;
    }
    #shortcuts {
        text-align: center;
        padding: 0 1;
        color: $text-muted;
    }
    #feedback {
        text-align: left;
        padding: 0 1;
        color: $success;
        height: 1;
    }
    DataTable {
        height: auto;
        max-height: 24;
    }
    """

    BINDINGS: ClassVar[list[BindingType]] = [
        Binding("j", "cursor_down", "Down", show=False),
        Binding("k", "cursor_up", "Up", show=False),
        Binding("p", "set_project", "Project"),
        Binding("d", "set_due", "Due date"),
        Binding("r", "set_priority", "Priority"),
        Binding("l", "set_label", "Label"),
        Binding("x", "mark_done", "Done"),
        Binding("u", "undo_last", "Undo"),
        Binding("h", "toggle_shortcuts", "Toggle shortcuts"),
        Binding("question_mark", "show_help", "Help"),
        Binding("q", "quit_review", "Quit"),
    ]

    def __init__(
        self,
        api: TodoistAPI,
        tasks: list[Task],
        projects: list[dict[str, str]],
        labels: list[str],
        title: str = "Inbox Review",
    ) -> None:
        super().__init__()
        self._api = api
        self._tasks = list(tasks)
        self._projects = projects
        self._labels = labels
        self._review_title = title
        self._stats = ReviewStats()
        self._show_shortcuts = True
        self._task_map: dict[str, Task] = {t.id: t for t in tasks}
        self._project_map: dict[str, str] = {p["id"]: p["name"] for p in projects}

    def compose(self) -> ComposeResult:
        yield Static(f"{self._review_title} ({len(self._tasks)} tasks)", id="header")
        table: DataTable[str] = DataTable(cursor_type="row", id="review-table")
        table.add_column(" ", key="status", width=3)
        table.add_column("#", key="num", width=3)
        table.add_column("Pri", key="pri", width=5)
        table.add_column("Content", key="content")
        table.add_column("Project", key="project")
        table.add_column("Due", key="due")
        table.add_column("Labels", key="labels")
        yield table
        yield Static("", id="feedback")
        yield Static("", id="status-line")
        yield Vertical(
            Static(
                "p project · d due · r priority · l label · x done\n"
                "u undo · h hide shortcuts · ? help · q quit",
                id="shortcuts",
            ),
        )

    def on_mount(self) -> None:
        self._refresh_table()
        self._update_status()

    def _refresh_table(self) -> None:
        table = self.query_one("#review-table", DataTable)
        table.clear()
        for i, task in enumerate(self._tasks, 1):
            status = ""
            if task.content in self._stats.completed:
                status = "✗"
            elif task.content in self._stats.updated:
                status = "✓"
            pri = _PRIORITY_LABELS.get(task.priority, "p4")
            project = self._project_map.get(task.project_id, "")
            due = task.due.string if task.due else ""
            labels = ", ".join(f"@{lbl}" for lbl in task.labels) if task.labels else ""
            table.add_row(status, str(i), pri, task.content, project, due, labels, key=task.id)

    def _update_status(self) -> None:
        remaining = len(self._tasks)
        updated = len(self._stats.updated)
        completed = len(self._stats.completed)
        status = self.query_one("#status-line", Static)
        status.update(f"✓ {updated} updated · ✗ {completed} done · {remaining} remaining")

    def _set_feedback(self, msg: str) -> None:
        self.query_one("#feedback", Static).update(f"✓ {msg}")

    def _get_selected_task(self) -> Task | None:
        table = self.query_one("#review-table", DataTable)
        if table.row_count == 0:
            return None
        row_key, _ = table.coordinate_to_cell_key(table.cursor_coordinate)
        return self._task_map.get(str(row_key))

    def action_cursor_down(self) -> None:
        self.query_one("#review-table", DataTable).action_cursor_down()

    def action_cursor_up(self) -> None:
        self.query_one("#review-table", DataTable).action_cursor_up()

    def action_set_project(self) -> None:
        task = self._get_selected_task()
        if not task:
            return

        def on_project(project_id: str | None) -> None:
            if project_id and task:
                self._api.move_task(task.id, project_id=project_id)
                project_name = self._project_map.get(project_id, "")
                task.project_id = project_id
                if task.content not in self._stats.updated:
                    self._stats.updated.append(task.content)
                self._stats.undo_stack.append(
                    {"action": "project", "task_id": task.id, "old_project": task.project_id}
                )
                self._set_feedback(f"{task.content} → {project_name}")
                self._refresh_table()
                self._update_status()

        self.push_screen(ProjectPickerScreen(self._projects), on_project)

    def action_set_due(self) -> None:
        task = self._get_selected_task()
        if not task:
            return

        def on_due(due_string: str | None) -> None:
            if due_string and task:
                self._api.update_task(task.id, due_string=due_string)
                if task.content not in self._stats.updated:
                    self._stats.updated.append(task.content)
                self._set_feedback(f"{task.content} → due {due_string}")
                self._refresh_table()
                self._update_status()

        self.push_screen(DueDateScreen(task.content), on_due)

    def action_set_priority(self) -> None:
        task = self._get_selected_task()
        if not task:
            return

        def on_priority(priority: int | None) -> None:
            if priority is not None and task:
                self._api.update_task(task.id, priority=priority)
                task.priority = priority
                if task.content not in self._stats.updated:
                    self._stats.updated.append(task.content)
                pri_label = _PRIORITY_LABELS.get(priority, "p4")
                self._set_feedback(f"{task.content} → {pri_label}")
                self._refresh_table()
                self._update_status()

        self.push_screen(PriorityPickerScreen(), on_priority)

    def action_set_label(self) -> None:
        task = self._get_selected_task()
        if not task:
            return

        def on_label(label_name: str | None) -> None:
            if label_name and task:
                new_labels = [*(task.labels or []), label_name]
                self._api.update_task(task.id, labels=new_labels)
                task.labels = new_labels
                if task.content not in self._stats.updated:
                    self._stats.updated.append(task.content)
                self._set_feedback(f"{task.content} → @{label_name}")
                self._refresh_table()
                self._update_status()

        self.push_screen(LabelPickerScreen(self._labels), on_label)

    def action_mark_done(self) -> None:
        task = self._get_selected_task()
        if not task:
            return

        self._api.complete_task(task.id)
        self._stats.completed.append(task.content)
        self._tasks.remove(task)
        del self._task_map[task.id]
        self._set_feedback(f"Completed: {task.content}")
        self._refresh_table()
        self._update_status()
        self.query_one("#header", Static).update(
            f"{self._review_title} ({len(self._tasks)} tasks)"
        )

    def action_undo_last(self) -> None:
        if not self._stats.undo_stack:
            self._set_feedback("Nothing to undo")
            return
        # Simple undo — just notify, full undo would need API revert
        self._stats.undo_stack.pop()
        self._set_feedback("Undo not yet implemented for API changes")

    def action_toggle_shortcuts(self) -> None:
        self._show_shortcuts = not self._show_shortcuts
        shortcuts = self.query_one("#shortcuts", Static)
        if self._show_shortcuts:
            shortcuts.update(
                "p project · d due · r priority · l label · x done\n"
                "u undo · h hide shortcuts · ? help · q quit"
            )
        else:
            shortcuts.update("h show shortcuts · ? help")

    def action_show_help(self) -> None:
        help_text = (
            "j/↓  Move down    k/↑  Move up\n"
            "p    Set project   d    Set due date\n"
            "r    Set priority  l    Add label\n"
            "x    Mark done     u    Undo last\n"
            "h    Toggle keys   q    Quit review"
        )
        self._set_feedback(help_text)

    def action_quit_review(self) -> None:
        self._stats.skipped = len(self._tasks)
        self.exit(self._stats)
