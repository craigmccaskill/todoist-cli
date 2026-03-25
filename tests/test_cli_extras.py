"""Tests for remaining CLI coverage gaps."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from td.cli import cli
from td.cli.errors import TdNotFoundError


def _mock_task(**overrides: object) -> MagicMock:
    task = MagicMock()
    task.id = overrides.get("id", "t1")
    task.content = overrides.get("content", "Buy milk")
    task.priority = overrides.get("priority", 1)
    task.labels = overrides.get("labels", [])
    task.due = None
    task.to_dict.return_value = {
        "id": task.id,
        "content": task.content,
        "priority": task.priority,
        "labels": task.labels,
        "due": None,
    }
    return task


class TestEditCommand:
    @patch("td.cli.tasks.get_client")
    def test_edit_task(self, mock_gc: MagicMock) -> None:
        api = MagicMock()
        mock_gc.return_value = api
        api.update_task.return_value = _mock_task(content="Updated")

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "edit", "t1", "--content", "Updated"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["ok"] is True

    @patch("td.cli.tasks.get_client")
    def test_edit_no_flags_shows_task(self, mock_gc: MagicMock) -> None:
        api = MagicMock()
        mock_gc.return_value = api
        api.get_task.return_value = _mock_task(content="Buy milk")

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "edit", "t1"])

        assert result.exit_code == 0
        api.get_task.assert_called_once_with("t1")
        api.update_task.assert_not_called()
        data = json.loads(result.output)
        assert data["ok"] is True

    @patch("td.cli.tasks.get_client")
    def test_edit_with_priority(self, mock_gc: MagicMock) -> None:
        api = MagicMock()
        mock_gc.return_value = api
        api.update_task.return_value = _mock_task()

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "edit", "t1", "--priority", "1"])

        assert result.exit_code == 0
        # Priority 1 (user) = 4 (API)
        _, kwargs = api.update_task.call_args
        assert kwargs["priority"] == 4


class TestDoneFuzzyConfirmation:
    @patch("td.cli.tasks.get_client")
    def test_done_fuzzy_with_yes_flag(self, mock_gc: MagicMock) -> None:
        api = MagicMock()
        mock_gc.return_value = api
        api.get_tasks.return_value = iter([[_mock_task(content="Buy milk")]])

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "done", "buy milk", "-y"])

        assert result.exit_code == 0
        api.complete_task.assert_called_once()

    @patch("td.cli.tasks.get_client")
    def test_done_row_number_no_confirmation(self, mock_gc: MagicMock) -> None:
        api = MagicMock()
        mock_gc.return_value = api

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "done", "t1"])

        assert result.exit_code == 0
        api.complete_task.assert_called_once_with("t1")


class TestUndoCommand:
    @patch("td.cli.tasks.get_client")
    def test_undo_task(self, mock_gc: MagicMock) -> None:
        api = MagicMock()
        mock_gc.return_value = api

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "undo", "t1"])

        assert result.exit_code == 0
        api.uncomplete_task.assert_called_once_with("t1")
        data = json.loads(result.output)
        assert data["ok"] is True


class TestDeleteCommand:
    @patch("td.cli.tasks.get_client")
    def test_delete_with_yes_flag(self, mock_gc: MagicMock) -> None:
        api = MagicMock()
        mock_gc.return_value = api

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "delete", "t1", "--yes"])

        assert result.exit_code == 0
        api.delete_task.assert_called_once_with("t1")


class TestErrorBoundary:
    @patch("td.cli.tasks.get_client")
    def test_td_error_caught(self, mock_gc: MagicMock) -> None:
        api = MagicMock()
        mock_gc.return_value = api
        api.complete_task.side_effect = TdNotFoundError(
            "Task not found",
            details={"task_id": "bad"},
        )

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "done", "bad"])

        assert result.exit_code == 1

    @patch("td.cli.tasks.get_client")
    def test_api_exception_caught(self, mock_gc: MagicMock) -> None:
        from requests import HTTPError

        api = MagicMock()
        mock_gc.return_value = api
        resp = MagicMock()
        resp.status_code = 404
        api.complete_task.side_effect = HTTPError(response=resp)

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "done", "bad"])

        assert result.exit_code == 1


class TestMoveCommand:
    @patch("td.cli.tasks.get_client")
    def test_move_task(self, mock_gc: MagicMock) -> None:
        api = MagicMock()
        mock_gc.return_value = api

        proj = MagicMock()
        proj.id = "p2"
        proj.name = "Personal"
        proj.is_inbox_project = False
        api.get_projects.return_value = iter([[proj]])
        api.move_task.return_value = True

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "move", "t1", "-p", "Personal"])

        assert result.exit_code == 0
        api.move_task.assert_called_once_with("t1", project_id="p2")
        data = json.loads(result.output)
        assert data["ok"] is True


class TestAddWithProject:
    @patch("td.cli.tasks.get_client")
    def test_add_with_project_resolution(self, mock_gc: MagicMock) -> None:
        api = MagicMock()
        mock_gc.return_value = api

        proj = MagicMock()
        proj.id = "p1"
        proj.name = "Work"
        proj.is_inbox_project = False
        api.get_projects.return_value = iter([[proj]])
        api.add_task.return_value = _mock_task()

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "add", "Test", "-p", "Work"])

        assert result.exit_code == 0
        _, kwargs = api.add_task.call_args
        assert kwargs["project_id"] == "p1"

    @patch("td.cli.tasks.get_client")
    def test_add_with_section(self, mock_gc: MagicMock) -> None:
        api = MagicMock()
        mock_gc.return_value = api

        proj = MagicMock()
        proj.id = "p1"
        proj.name = "Work"
        proj.is_inbox_project = False
        api.get_projects.return_value = iter([[proj]])

        sec = MagicMock()
        sec.id = "s1"
        sec.name = "In Progress"
        api.get_sections.return_value = iter([[sec]])

        api.add_task.return_value = _mock_task()

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "add", "Test", "-p", "Work", "-s", "In Progress"])

        assert result.exit_code == 0
        _, kwargs = api.add_task.call_args
        assert kwargs["section_id"] == "s1"

    @patch("td.cli.tasks.get_client")
    def test_add_section_without_project_errors(self, mock_gc: MagicMock) -> None:
        api = MagicMock()
        mock_gc.return_value = api

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "add", "Test", "-s", "Backlog"])

        assert result.exit_code == 1
