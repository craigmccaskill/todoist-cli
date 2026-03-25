"""Tests for TUI infrastructure."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from td.tui import is_available


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

    @pytest.mark.asyncio
    async def test_review_app_creates(self) -> None:
        from td.tui.review import ReviewApp

        api = MagicMock()
        task = MagicMock()
        task.id = "t1"
        task.content = "Test task"
        task.priority = 1
        task.labels = []
        task.project_id = "p1"
        task.due = None

        app = ReviewApp(
            api=api,
            tasks=[task],
            projects=[{"id": "p1", "name": "Work"}],
            labels=["urgent"],
            title="Test Review",
        )
        assert app is not None

    @pytest.mark.asyncio
    async def test_review_app_quit(self) -> None:
        from td.tui.review import ReviewApp

        api = MagicMock()
        task = MagicMock()
        task.id = "t1"
        task.content = "Test task"
        task.priority = 1
        task.labels = []
        task.project_id = "p1"
        task.due = None

        app = ReviewApp(
            api=api,
            tasks=[task],
            projects=[{"id": "p1", "name": "Work"}],
            labels=["urgent"],
        )
        async with app.run_test() as pilot:
            await pilot.pause()
            await pilot.press("q")

        assert app.return_value is not None
        assert app.return_value.skipped == 1

    @pytest.mark.asyncio
    async def test_review_app_navigation(self) -> None:
        from td.tui.review import ReviewApp

        api = MagicMock()
        tasks = []
        for i, name in enumerate(["Task A", "Task B"]):
            t = MagicMock()
            t.id = f"t{i}"
            t.content = name
            t.priority = 1
            t.labels = []
            t.project_id = "p1"
            t.due = None
            tasks.append(t)

        app = ReviewApp(
            api=api,
            tasks=tasks,
            projects=[{"id": "p1", "name": "Work"}],
            labels=["urgent"],
        )
        async with app.run_test() as pilot:
            await pilot.pause()
            await pilot.press("j")  # move down
            await pilot.press("k")  # move up
            await pilot.press("q")

        assert app.return_value is not None


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
