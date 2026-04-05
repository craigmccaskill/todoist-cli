"""Tests for TUI infrastructure."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from td.tui import is_available


def _make_task(
    task_id: str = "t1",
    content: str = "Test task",
    priority: int = 1,
    project_id: str = "p1",
    labels: list[str] | None = None,
    due: object | None = None,
    description: str = "",
) -> MagicMock:
    """Create a mock Task with standard attributes."""
    task = MagicMock()
    task.id = task_id
    task.content = content
    task.priority = priority
    task.project_id = project_id
    task.labels = labels if labels is not None else []
    task.due = due
    task.description = description
    return task


def _make_review_app(
    tasks: list[MagicMock] | None = None,
    projects: list[dict[str, str]] | None = None,
    labels: list[str] | None = None,
    title: str = "Test Review",
) -> tuple[MagicMock, object]:
    """Create a ReviewApp with defaults for testing."""
    from td.tui.review import ReviewApp

    api = MagicMock()
    if tasks is None:
        tasks = [_make_task()]
    if projects is None:
        projects = [{"id": "p1", "name": "Work"}, {"id": "p2", "name": "Personal"}]
    if labels is None:
        labels = ["urgent", "waiting"]

    app = ReviewApp(
        api=api,
        tasks=tasks,
        projects=projects,
        labels=labels,
        title=title,
    )
    return api, app


class TestTuiAvailability:
    def test_is_available(self) -> None:
        assert is_available() is True

    def test_picker_imports(self) -> None:
        from td.tui.picker import PickerApp, pick_from_list

        assert PickerApp is not None
        assert pick_from_list is not None

    def test_domain_pickers_import(self) -> None:
        from td.tui.pickers import (
            pick_label,
            pick_priority,
            pick_project,
            pick_section,
            pick_task,
        )

        assert pick_task is not None
        assert pick_project is not None
        assert pick_label is not None
        assert pick_section is not None
        assert pick_priority is not None


# ---------------------------------------------------------------------------
# PickerApp core tests
# ---------------------------------------------------------------------------


class TestPickerApp:
    @pytest.mark.asyncio
    async def test_picker_app_creates(self) -> None:
        """Verify PickerApp can be instantiated with test data."""
        from td.tui.picker import PickerApp

        app = PickerApp(
            title="Test",
            columns=["Name", "Value"],
            rows=[
                {"id": "1", "Name": "Alpha", "Value": "100"},
                {"id": "2", "Name": "Beta", "Value": "200"},
            ],
        )
        assert app is not None

    @pytest.mark.asyncio
    async def test_picker_app_cancel(self) -> None:
        """Verify cancel returns None."""
        from textual.pilot import Pilot

        from td.tui.picker import PickerApp

        app = PickerApp(
            title="Test",
            columns=["Name"],
            rows=[{"id": "1", "Name": "Alpha"}],
        )
        async with app.run_test() as pilot:
            assert isinstance(pilot, Pilot)
            await pilot.press("escape")

        assert app.return_value is None

    @pytest.mark.asyncio
    async def test_picker_app_select(self) -> None:
        """Verify enter returns the selected key."""
        from td.tui.picker import PickerApp

        app = PickerApp(
            title="Test",
            columns=["Name"],
            rows=[
                {"id": "first", "Name": "Alpha"},
                {"id": "second", "Name": "Beta"},
            ],
        )
        async with app.run_test() as pilot:
            await pilot.press("enter")

        assert app.return_value == "first"

    @pytest.mark.asyncio
    async def test_picker_app_navigate_and_select(self) -> None:
        """Verify navigating down then selecting returns second row."""
        from td.tui.picker import PickerApp

        app = PickerApp(
            title="Test",
            columns=["Name"],
            rows=[
                {"id": "first", "Name": "Alpha"},
                {"id": "second", "Name": "Beta"},
            ],
        )
        async with app.run_test() as pilot:
            await pilot.press("down")
            await pilot.press("enter")

        assert app.return_value == "second"

    @pytest.mark.asyncio
    async def test_picker_app_empty_list_select(self) -> None:
        """Verify selecting from empty list returns None."""
        from td.tui.picker import PickerApp

        app = PickerApp(
            title="Test",
            columns=["Name"],
            rows=[],
        )
        async with app.run_test() as pilot:
            await pilot.press("enter")

        assert app.return_value is None


# ---------------------------------------------------------------------------
# PickerApp filter tests
# ---------------------------------------------------------------------------


class TestPickerFilter:
    @pytest.mark.asyncio
    async def test_picker_filter_opens(self) -> None:
        """Press / to open filter input."""
        from td.tui.picker import PickerApp

        app = PickerApp(
            title="Test",
            columns=["Name"],
            rows=[{"id": "1", "Name": "Alpha"}, {"id": "2", "Name": "Beta"}],
        )
        async with app.run_test() as pilot:
            await pilot.press("slash")
            await pilot.pause()
            assert app._filter_active is True
            filter_input = app.query_one("#filter-input")
            assert "visible" in filter_input.classes
            await pilot.press("escape")

    @pytest.mark.asyncio
    async def test_picker_filter_narrows(self) -> None:
        """Type text in filter, rows reduce."""
        from textual.widgets import DataTable

        from td.tui.picker import PickerApp

        app = PickerApp(
            title="Test",
            columns=["Name"],
            rows=[
                {"id": "1", "Name": "Alpha"},
                {"id": "2", "Name": "Beta"},
                {"id": "3", "Name": "Gamma"},
            ],
        )
        async with app.run_test() as pilot:
            await pilot.press("slash")
            await pilot.pause()
            await pilot.press("a", "l", "p", "h", "a")
            await pilot.pause()
            table = app.query_one(DataTable)
            assert table.row_count == 1
            await pilot.press("escape")

    @pytest.mark.asyncio
    async def test_picker_filter_escape_closes(self) -> None:
        """Escape in filter restores all rows and hides filter."""
        from textual.widgets import DataTable

        from td.tui.picker import PickerApp

        app = PickerApp(
            title="Test",
            columns=["Name"],
            rows=[
                {"id": "1", "Name": "Alpha"},
                {"id": "2", "Name": "Beta"},
            ],
        )
        async with app.run_test() as pilot:
            await pilot.press("slash")
            await pilot.pause()
            await pilot.press("a", "l", "p")
            await pilot.pause()
            table = app.query_one(DataTable)
            assert table.row_count == 1
            # Escape closes filter and restores rows
            await pilot.press("escape")
            await pilot.pause()
            assert app._filter_active is False
            assert table.row_count == 2
            # Now escape again should cancel the picker
            await pilot.press("escape")

    @pytest.mark.asyncio
    async def test_picker_filter_submit_refocuses(self) -> None:
        """Enter in filter refocuses the table, then enter selects."""
        from textual.widgets import DataTable

        from td.tui.picker import PickerApp

        app = PickerApp(
            title="Test",
            columns=["Name"],
            rows=[
                {"id": "1", "Name": "Alpha"},
                {"id": "2", "Name": "Beta"},
            ],
        )
        async with app.run_test() as pilot:
            await pilot.press("slash")
            await pilot.pause()
            # Press enter in filter to refocus table
            await pilot.press("enter")
            await pilot.pause()
            table = app.query_one(DataTable)
            assert table.has_focus
            # Now escape to exit
            await pilot.press("escape")


# ---------------------------------------------------------------------------
# Domain pickers (pickers.py) — tested via PickerApp directly
# ---------------------------------------------------------------------------


class TestPickTask:
    @pytest.mark.asyncio
    async def test_pick_task_select(self) -> None:
        """pick_task builds correct rows and selecting returns task ID."""
        from td.tui.picker import PickerApp
        from td.tui.pickers import _PRIORITY_LABELS

        task = _make_task(task_id="task-1", content="Buy milk", priority=4)
        task.due = MagicMock()
        task.due.string = "2026-04-10"
        task.labels = ["shopping"]

        # Build rows the same way pick_task does, then test via PickerApp
        rows = [
            {
                "id": task.id,
                "#": "1",
                "Pri": _PRIORITY_LABELS.get(task.priority, "p4"),
                "Content": task.content,
                "Due": task.due.string,
                "Labels": "@shopping",
            }
        ]
        app = PickerApp(
            title="Select a task",
            columns=["#", "Pri", "Content", "Due", "Labels"],
            rows=rows,
        )
        async with app.run_test() as pilot:
            await pilot.press("enter")

        assert app.return_value == "task-1"

    @pytest.mark.asyncio
    async def test_pick_task_cancel(self) -> None:
        """Cancelling task picker returns None."""
        from td.tui.picker import PickerApp

        rows = [{"id": "t1", "#": "1", "Pri": "p4", "Content": "Test", "Due": "", "Labels": ""}]
        app = PickerApp(
            title="Select a task",
            columns=["#", "Pri", "Content", "Due", "Labels"],
            rows=rows,
        )
        async with app.run_test() as pilot:
            await pilot.press("escape")

        assert app.return_value is None

    @pytest.mark.asyncio
    async def test_pick_task_navigate_and_select(self) -> None:
        """Navigate down and select second task."""
        from td.tui.picker import PickerApp

        rows = [
            {"id": "t1", "#": "1", "Pri": "p4", "Content": "First", "Due": "", "Labels": ""},
            {"id": "t2", "#": "2", "Pri": "p4", "Content": "Second", "Due": "", "Labels": ""},
        ]
        app = PickerApp(
            title="Select a task",
            columns=["#", "Pri", "Content", "Due", "Labels"],
            rows=rows,
        )
        async with app.run_test() as pilot:
            await pilot.press("down")
            await pilot.press("enter")

        assert app.return_value == "t2"

    @pytest.mark.asyncio
    async def test_pick_task_empty_list(self) -> None:
        """Empty task list returns None on enter."""
        from td.tui.picker import PickerApp

        app = PickerApp(
            title="Select a task",
            columns=["#", "Pri", "Content", "Due", "Labels"],
            rows=[],
        )
        async with app.run_test() as pilot:
            await pilot.press("enter")

        assert app.return_value is None


class TestPickProject:
    @pytest.mark.asyncio
    async def test_pick_project_select(self) -> None:
        """Selecting a project returns its ID."""
        from td.tui.picker import PickerApp

        rows = [
            {"id": "p1", "Name": "Work", " ": ""},
            {"id": "p2", "Name": "Personal", " ": ""},
        ]
        app = PickerApp(title="Select a project", columns=["Name", " "], rows=rows)
        async with app.run_test() as pilot:
            await pilot.press("enter")

        assert app.return_value == "p1"

    @pytest.mark.asyncio
    async def test_pick_project_cancel(self) -> None:
        """Cancelling project picker returns None."""
        from td.tui.picker import PickerApp

        rows = [{"id": "p1", "Name": "Work", " ": ""}]
        app = PickerApp(title="Select a project", columns=["Name", " "], rows=rows)
        async with app.run_test() as pilot:
            await pilot.press("escape")

        assert app.return_value is None

    @pytest.mark.asyncio
    async def test_pick_project_favorites_display(self) -> None:
        """Favorite projects show star in display column."""
        from textual.widgets import DataTable

        from td.tui.picker import PickerApp

        rows = [
            {"id": "p1", "Name": "Work", " ": "\u2605"},
            {"id": "p2", "Name": "Personal", " ": ""},
        ]
        app = PickerApp(title="Select a project", columns=["Name", " "], rows=rows)
        async with app.run_test() as pilot:
            await pilot.pause()
            table = app.query_one(DataTable)
            assert table.row_count == 2
            await pilot.press("escape")


class TestPickLabel:
    @pytest.mark.asyncio
    async def test_pick_label_select(self) -> None:
        """Selecting a label returns label name."""
        from td.tui.picker import PickerApp

        rows = [
            {"id": "urgent", "Name": "@urgent"},
            {"id": "waiting", "Name": "@waiting"},
        ]
        app = PickerApp(title="Select a label", columns=["Name"], rows=rows)
        async with app.run_test() as pilot:
            await pilot.press("enter")

        assert app.return_value == "urgent"

    @pytest.mark.asyncio
    async def test_pick_label_cancel(self) -> None:
        """Cancelling label picker returns None."""
        from td.tui.picker import PickerApp

        rows = [{"id": "urgent", "Name": "@urgent"}]
        app = PickerApp(title="Select a label", columns=["Name"], rows=rows)
        async with app.run_test() as pilot:
            await pilot.press("escape")

        assert app.return_value is None

    @pytest.mark.asyncio
    async def test_pick_label_at_prefix_display(self) -> None:
        """Labels are displayed with @ prefix."""
        from textual.widgets import DataTable

        from td.tui.picker import PickerApp

        rows = [{"id": "urgent", "Name": "@urgent"}]
        app = PickerApp(title="Select a label", columns=["Name"], rows=rows)
        async with app.run_test() as pilot:
            await pilot.pause()
            table = app.query_one(DataTable)
            assert table.row_count == 1
            await pilot.press("escape")


class TestPickSection:
    @pytest.mark.asyncio
    async def test_pick_section_select(self) -> None:
        """Selecting a section returns section ID."""
        from td.tui.picker import PickerApp

        rows = [
            {"id": "s1", "Name": "Backlog"},
            {"id": "s2", "Name": "In Progress"},
        ]
        app = PickerApp(title="Select a section", columns=["Name"], rows=rows)
        async with app.run_test() as pilot:
            await pilot.press("enter")

        assert app.return_value == "s1"

    @pytest.mark.asyncio
    async def test_pick_section_cancel(self) -> None:
        """Cancelling section picker returns None."""
        from td.tui.picker import PickerApp

        rows = [{"id": "s1", "Name": "Backlog"}]
        app = PickerApp(title="Select a section", columns=["Name"], rows=rows)
        async with app.run_test() as pilot:
            await pilot.press("escape")

        assert app.return_value is None


class TestPickPriority:
    @pytest.mark.asyncio
    async def test_pick_priority_select_returns_int(self) -> None:
        """Selecting p1 returns API priority 4 (int)."""
        from td.tui.picker import PickerApp

        rows = [
            {"id": "4", "Priority": "p1 \u2014 Urgent"},
            {"id": "3", "Priority": "p2 \u2014 High"},
            {"id": "2", "Priority": "p3 \u2014 Medium"},
            {"id": "1", "Priority": "p4 \u2014 Low"},
        ]
        app = PickerApp(title="Select priority", columns=["Priority"], rows=rows)
        async with app.run_test() as pilot:
            await pilot.press("enter")

        # PickerApp returns string; pick_priority converts to int
        assert app.return_value == "4"
        assert int(app.return_value) == 4

    @pytest.mark.asyncio
    async def test_pick_priority_cancel_returns_none(self) -> None:
        """Cancelling priority picker returns None."""
        from td.tui.picker import PickerApp

        rows = [
            {"id": "4", "Priority": "p1 \u2014 Urgent"},
            {"id": "3", "Priority": "p2 \u2014 High"},
            {"id": "2", "Priority": "p3 \u2014 Medium"},
            {"id": "1", "Priority": "p4 \u2014 Low"},
        ]
        app = PickerApp(title="Select priority", columns=["Priority"], rows=rows)
        async with app.run_test() as pilot:
            await pilot.press("escape")

        assert app.return_value is None

    @pytest.mark.asyncio
    async def test_pick_priority_all_four_options(self) -> None:
        """All four priority options are present."""
        from textual.widgets import DataTable

        from td.tui.picker import PickerApp

        rows = [
            {"id": "4", "Priority": "p1 \u2014 Urgent"},
            {"id": "3", "Priority": "p2 \u2014 High"},
            {"id": "2", "Priority": "p3 \u2014 Medium"},
            {"id": "1", "Priority": "p4 \u2014 Low"},
        ]
        app = PickerApp(title="Select priority", columns=["Priority"], rows=rows)
        async with app.run_test() as pilot:
            await pilot.pause()
            table = app.query_one(DataTable)
            assert table.row_count == 4
            await pilot.press("escape")


# ---------------------------------------------------------------------------
# Modal screens (review.py)
# ---------------------------------------------------------------------------


class TestProjectPickerScreen:
    @pytest.mark.asyncio
    async def test_project_picker_cancel(self) -> None:
        """Escape dismisses with None."""
        from td.tui.review import ProjectPickerScreen

        _api, app = _make_review_app()
        result = None

        async with app.run_test() as pilot:
            await pilot.pause()

            def capture(value: str | None) -> None:
                nonlocal result
                result = value

            app.push_screen(
                ProjectPickerScreen([{"id": "p1", "name": "Work"}]),
                capture,
            )
            await pilot.pause()
            await pilot.press("escape")
            await pilot.pause()
            await pilot.press("q")

        assert result is None

    @pytest.mark.asyncio
    async def test_project_picker_enter_binding(self) -> None:
        """Enter binding selects the focused row."""
        from td.tui.review import ProjectPickerScreen

        _api, app = _make_review_app()
        result = "not-set"

        async with app.run_test() as pilot:
            await pilot.pause()

            def capture(value: str | None) -> None:
                nonlocal result
                result = value

            app.push_screen(
                ProjectPickerScreen(
                    [{"id": "p1", "name": "Work"}, {"id": "p2", "name": "Personal"}]
                ),
                capture,
            )
            await pilot.pause()
            await pilot.press("enter")
            await pilot.pause()
            await pilot.press("q")

        assert result == "p1"


class TestPriorityPickerScreen:
    @pytest.mark.asyncio
    async def test_priority_picker_select_returns_int(self) -> None:
        """Selecting priority returns an int."""
        from td.tui.review import PriorityPickerScreen

        _api, app = _make_review_app()
        result = "not-set"

        async with app.run_test() as pilot:
            await pilot.pause()

            def capture(value: int | None) -> None:
                nonlocal result
                result = value  # type: ignore[assignment]

            app.push_screen(PriorityPickerScreen(), capture)
            await pilot.pause()
            await pilot.press("enter")
            await pilot.pause()
            await pilot.press("q")

        assert isinstance(result, int)
        assert result == 4  # First row is p1 = API priority 4

    @pytest.mark.asyncio
    async def test_priority_picker_cancel(self) -> None:
        """Escape dismisses with None."""
        from td.tui.review import PriorityPickerScreen

        _api, app = _make_review_app()
        result = "not-set"

        async with app.run_test() as pilot:
            await pilot.pause()

            def capture(value: int | None) -> None:
                nonlocal result
                result = value  # type: ignore[assignment]

            app.push_screen(PriorityPickerScreen(), capture)
            await pilot.pause()
            await pilot.press("escape")
            await pilot.pause()
            await pilot.press("q")

        assert result is None


class TestLabelPickerScreen:
    @pytest.mark.asyncio
    async def test_label_picker_select(self) -> None:
        """Selecting a label returns label name string."""
        from td.tui.review import LabelPickerScreen

        _api, app = _make_review_app()
        result = "not-set"

        async with app.run_test() as pilot:
            await pilot.pause()

            def capture(value: str | None) -> None:
                nonlocal result
                result = value  # type: ignore[assignment]

            app.push_screen(LabelPickerScreen(["urgent", "waiting"]), capture)
            await pilot.pause()
            await pilot.press("enter")
            await pilot.pause()
            await pilot.press("q")

        assert result == "urgent"

    @pytest.mark.asyncio
    async def test_label_picker_cancel(self) -> None:
        """Escape dismisses with None."""
        from td.tui.review import LabelPickerScreen

        _api, app = _make_review_app()
        result = "not-set"

        async with app.run_test() as pilot:
            await pilot.pause()

            def capture(value: str | None) -> None:
                nonlocal result
                result = value  # type: ignore[assignment]

            app.push_screen(LabelPickerScreen(["urgent"]), capture)
            await pilot.pause()
            await pilot.press("escape")
            await pilot.pause()
            await pilot.press("q")

        assert result is None


class TestDueDateScreen:
    @pytest.mark.asyncio
    async def test_due_date_submit(self) -> None:
        """Typing a date and pressing enter returns the date string."""
        from td.tui.review import DueDateScreen

        _api, app = _make_review_app()
        result = "not-set"

        async with app.run_test() as pilot:
            await pilot.pause()

            def capture(value: str | None) -> None:
                nonlocal result
                result = value  # type: ignore[assignment]

            app.push_screen(DueDateScreen("Test task"), capture)
            await pilot.pause()
            await pilot.press("t", "o", "m", "o", "r", "r", "o", "w")
            await pilot.press("enter")
            await pilot.pause()
            await pilot.press("q")

        assert result == "tomorrow"

    @pytest.mark.asyncio
    async def test_due_date_cancel(self) -> None:
        """Escape dismisses with None."""
        from td.tui.review import DueDateScreen

        _api, app = _make_review_app()
        result = "not-set"

        async with app.run_test() as pilot:
            await pilot.pause()

            def capture(value: str | None) -> None:
                nonlocal result
                result = value  # type: ignore[assignment]

            app.push_screen(DueDateScreen("Test task"), capture)
            await pilot.pause()
            await pilot.press("escape")
            await pilot.pause()
            await pilot.press("q")

        assert result is None

    @pytest.mark.asyncio
    async def test_due_date_empty_input(self) -> None:
        """Submitting empty input returns None."""
        from td.tui.review import DueDateScreen

        _api, app = _make_review_app()
        result = "not-set"

        async with app.run_test() as pilot:
            await pilot.pause()

            def capture(value: str | None) -> None:
                nonlocal result
                result = value  # type: ignore[assignment]

            app.push_screen(DueDateScreen("Test task"), capture)
            await pilot.pause()
            await pilot.press("enter")
            await pilot.pause()
            await pilot.press("q")

        assert result is None


# ---------------------------------------------------------------------------
# ReviewApp tests
# ---------------------------------------------------------------------------


class TestReviewCommand:
    def test_review_non_tty_errors(self) -> None:
        from click.testing import CliRunner

        from td.cli import cli

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "review"])

        assert result.exit_code == 1

    def test_review_stats_dataclass(self) -> None:
        from td.tui.review import ReviewStats

        stats = ReviewStats()
        assert stats.updated == []
        assert stats.completed == []
        assert stats.skipped == 0
        assert stats.undo_stack == []

    def test_undo_entry_dataclass(self) -> None:
        from td.tui.review import UndoEntry

        entry = UndoEntry(
            action="project",
            task_id="t1",
            task_content="Test",
            old_project_id="p1",
        )
        assert entry.action == "project"
        assert entry.task_id == "t1"
        assert entry.old_project_id == "p1"
        assert entry.old_priority is None
        assert entry.old_labels is None
        assert entry.old_due_string is None
        assert entry.task is None

    @pytest.mark.asyncio
    async def test_review_app_creates(self) -> None:
        _api, app = _make_review_app()
        assert app is not None

    @pytest.mark.asyncio
    async def test_review_app_quit(self) -> None:
        _api, app = _make_review_app()
        async with app.run_test() as pilot:
            await pilot.pause()
            await pilot.press("q")

        assert app.return_value is not None
        assert app.return_value.skipped == 1

    @pytest.mark.asyncio
    async def test_review_app_navigation(self) -> None:
        tasks = [
            _make_task(task_id="t0", content="Task A"),
            _make_task(task_id="t1", content="Task B"),
        ]
        _api, app = _make_review_app(tasks=tasks)
        async with app.run_test() as pilot:
            await pilot.pause()
            await pilot.press("j")  # move down
            await pilot.press("k")  # move up
            await pilot.press("q")

        assert app.return_value is not None


class TestReviewActions:
    @pytest.mark.asyncio
    async def test_mark_done(self) -> None:
        """Press x to mark task done, verify API called and task removed."""
        task = _make_task(task_id="t1", content="Do laundry")
        api, app = _make_review_app(tasks=[task])

        async with app.run_test() as pilot:
            await pilot.pause()
            await pilot.press("x")
            await pilot.pause()
            await pilot.press("q")

        api.complete_task.assert_called_once_with("t1")
        assert app.return_value is not None
        assert "Do laundry" in app.return_value.completed
        assert app.return_value.skipped == 0  # task was removed

    @pytest.mark.asyncio
    async def test_toggle_shortcuts(self) -> None:
        """Press h to toggle shortcut visibility."""
        from textual.widgets import Static

        _api, app = _make_review_app()
        async with app.run_test() as pilot:
            await pilot.pause()
            # Initially shortcuts are visible
            assert app._show_shortcuts is True
            await pilot.press("h")
            await pilot.pause()
            assert app._show_shortcuts is False
            shortcuts = app.query_one("#shortcuts", Static)
            rendered = str(shortcuts.content)
            assert "show shortcuts" in rendered
            # Toggle back
            await pilot.press("h")
            await pilot.pause()
            assert app._show_shortcuts is True
            await pilot.press("q")

    @pytest.mark.asyncio
    async def test_show_help(self) -> None:
        """Press ? to show help text in feedback."""
        from textual.widgets import Static

        _api, app = _make_review_app()
        async with app.run_test() as pilot:
            await pilot.pause()
            await pilot.press("question_mark")
            await pilot.pause()
            feedback = app.query_one("#feedback", Static)
            rendered = str(feedback.content)
            assert "Set project" in rendered
            assert "Mark done" in rendered
            await pilot.press("q")

    @pytest.mark.asyncio
    async def test_undo_nothing(self) -> None:
        """Press u with empty undo stack shows message."""
        from textual.widgets import Static

        _api, app = _make_review_app()
        async with app.run_test() as pilot:
            await pilot.pause()
            await pilot.press("u")
            await pilot.pause()
            feedback = app.query_one("#feedback", Static)
            rendered = str(feedback.content)
            assert "Nothing to undo" in rendered
            await pilot.press("q")

    @pytest.mark.asyncio
    async def test_undo_after_mark_done(self) -> None:
        """Mark done then undo restores the task."""
        task = _make_task(task_id="t1", content="Undo me")
        api, app = _make_review_app(tasks=[task])

        async with app.run_test() as pilot:
            await pilot.pause()
            await pilot.press("x")  # mark done
            await pilot.pause()
            assert len(app._tasks) == 0
            await pilot.press("u")  # undo
            await pilot.pause()
            assert len(app._tasks) == 1
            api.uncomplete_task.assert_called_once_with("t1")
            await pilot.press("q")

    @pytest.mark.asyncio
    async def test_empty_task_list(self) -> None:
        """ReviewApp with empty task list quits immediately with 0 skipped."""
        _api, app = _make_review_app(tasks=[])

        async with app.run_test() as pilot:
            await pilot.pause()
            await pilot.press("q")

        assert app.return_value is not None
        assert app.return_value.skipped == 0

    @pytest.mark.asyncio
    async def test_set_project_via_modal(self) -> None:
        """Press p, select project in modal, verify API call."""
        task = _make_task(task_id="t1", content="Move me")
        api, app = _make_review_app(tasks=[task])

        async with app.run_test() as pilot:
            await pilot.pause()
            await pilot.press("p")  # open project picker
            await pilot.pause()
            await pilot.press("enter")  # select first project
            await pilot.pause()
            await pilot.press("q")

        api.move_task.assert_called_once_with("t1", project_id="p1")
        assert app.return_value is not None
        assert "Move me" in app.return_value.updated

    @pytest.mark.asyncio
    async def test_set_priority_via_modal(self) -> None:
        """Press r, select priority in modal, verify API call."""
        task = _make_task(task_id="t1", content="Prioritize me", priority=1)
        api, app = _make_review_app(tasks=[task])

        async with app.run_test() as pilot:
            await pilot.pause()
            await pilot.press("r")  # open priority picker
            await pilot.pause()
            await pilot.press("enter")  # select p1 (API value 4)
            await pilot.pause()
            await pilot.press("q")

        api.update_task.assert_called_once_with("t1", priority=4)
        assert app.return_value is not None
        assert "Prioritize me" in app.return_value.updated

    @pytest.mark.asyncio
    async def test_set_label_via_modal(self) -> None:
        """Press l, select label in modal, verify API call."""
        task = _make_task(task_id="t1", content="Label me", labels=[])
        api, app = _make_review_app(tasks=[task])

        async with app.run_test() as pilot:
            await pilot.pause()
            await pilot.press("l")  # open label picker
            await pilot.pause()
            await pilot.press("enter")  # select first label ("urgent")
            await pilot.pause()
            await pilot.press("q")

        api.update_task.assert_called_once_with("t1", labels=["urgent"])
        assert app.return_value is not None
        assert "Label me" in app.return_value.updated

    @pytest.mark.asyncio
    async def test_set_due_via_modal(self) -> None:
        """Press d, enter date in modal, verify API call."""
        task = _make_task(task_id="t1", content="Schedule me")
        api, app = _make_review_app(tasks=[task])

        async with app.run_test() as pilot:
            await pilot.pause()
            await pilot.press("d")  # open due date screen
            await pilot.pause()
            await pilot.press("t", "o", "m", "o", "r", "r", "o", "w")
            await pilot.press("enter")
            await pilot.pause()
            await pilot.press("q")

        api.update_task.assert_called_once_with("t1", due_string="tomorrow")
        assert app.return_value is not None
        assert "Schedule me" in app.return_value.updated

    @pytest.mark.asyncio
    async def test_undo_project_change(self) -> None:
        """Undo project change reverts API call."""
        task = _make_task(task_id="t1", content="Move me", project_id="p1")
        api, app = _make_review_app(tasks=[task])

        async with app.run_test() as pilot:
            await pilot.pause()
            await pilot.press("p")  # set project
            await pilot.pause()
            # Navigate to second project
            await pilot.press("down")
            await pilot.press("enter")  # select p2
            await pilot.pause()
            await pilot.press("u")  # undo
            await pilot.pause()
            await pilot.press("q")

        # Should have called move_task twice: once to p2, once to undo back to p1
        assert api.move_task.call_count == 2

    @pytest.mark.asyncio
    async def test_undo_priority_change(self) -> None:
        """Undo priority change reverts API call."""
        task = _make_task(task_id="t1", content="Reprioritize", priority=1)
        api, app = _make_review_app(tasks=[task])

        async with app.run_test() as pilot:
            await pilot.pause()
            await pilot.press("r")  # set priority
            await pilot.pause()
            await pilot.press("enter")  # select p1 (API 4)
            await pilot.pause()
            await pilot.press("u")  # undo
            await pilot.pause()
            await pilot.press("q")

        # update_task called twice: set to 4, then undo back to 1
        assert api.update_task.call_count == 2

    @pytest.mark.asyncio
    async def test_undo_label_change(self) -> None:
        """Undo label change reverts API call."""
        task = _make_task(task_id="t1", content="Relabel", labels=[])
        api, app = _make_review_app(tasks=[task])

        async with app.run_test() as pilot:
            await pilot.pause()
            await pilot.press("l")  # set label
            await pilot.pause()
            await pilot.press("enter")  # select "urgent"
            await pilot.pause()
            await pilot.press("u")  # undo
            await pilot.pause()
            await pilot.press("q")

        # update_task called twice: add label, then undo
        assert api.update_task.call_count == 2

    @pytest.mark.asyncio
    async def test_actions_on_empty_table_are_noop(self) -> None:
        """Pressing action keys on an empty table does not crash."""
        api, app = _make_review_app(tasks=[])

        async with app.run_test() as pilot:
            await pilot.pause()
            await pilot.press("p")
            await pilot.press("d")
            await pilot.press("r")
            await pilot.press("l")
            await pilot.press("x")
            await pilot.pause()
            await pilot.press("q")

        # No API calls should have been made
        api.move_task.assert_not_called()
        api.update_task.assert_not_called()
        api.complete_task.assert_not_called()


class TestSelectModeFallback:
    """Test that commands error properly when no ref given in non-TTY."""

    @patch("td.cli.tasks.get_client")
    def test_done_no_ref_non_tty_errors(self, mock_gc: MagicMock) -> None:
        from click.testing import CliRunner

        from td.cli import cli

        api = MagicMock()
        mock_gc.return_value = api

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "done"])

        assert result.exit_code == 1

    @patch("td.cli.tasks.get_client")
    def test_show_no_ref_non_tty_errors(self, mock_gc: MagicMock) -> None:
        from click.testing import CliRunner

        from td.cli import cli

        api = MagicMock()
        mock_gc.return_value = api

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "show"])

        assert result.exit_code == 1
