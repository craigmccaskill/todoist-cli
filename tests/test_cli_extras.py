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
        result = runner.invoke(
            cli, ["--json", "edit", "t1", "--content", "Updated"]
        )

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["ok"] is True

    @patch("td.cli.tasks.get_client")
    def test_edit_with_priority(self, mock_gc: MagicMock) -> None:
        api = MagicMock()
        mock_gc.return_value = api
        api.update_task.return_value = _mock_task()

        runner = CliRunner()
        result = runner.invoke(
            cli, ["--json", "edit", "t1", "--priority", "1"]
        )

        assert result.exit_code == 0
        # Priority 1 (user) = 4 (API)
        _, kwargs = api.update_task.call_args
        assert kwargs["priority"] == 4


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
        result = runner.invoke(
            cli, ["--json", "add", "Test", "-p", "Work"]
        )

        assert result.exit_code == 0
        _, kwargs = api.add_task.call_args
        assert kwargs["project_id"] == "p1"
