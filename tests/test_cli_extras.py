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


class TestShowCommand:
    @patch("td.cli.tasks.get_client")
    def test_show_task(self, mock_gc: MagicMock) -> None:
        api = MagicMock()
        mock_gc.return_value = api
        task = _mock_task(content="Buy milk", description="Whole milk from store")
        api.get_task.return_value = task
        proj = MagicMock()
        proj.id = "p1"
        proj.name = "Personal"
        proj.is_inbox_project = False
        proj.to_dict.return_value = {"id": "p1", "name": "Personal"}
        api.get_projects.return_value = iter([[proj]])

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "show", "t1"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["ok"] is True
        assert data["data"]["content"] == "Buy milk"
        api.get_task.assert_called_once_with("t1")


class TestCommentCommand:
    @patch("td.cli.comments.get_client")
    def test_add_comment(self, mock_gc: MagicMock) -> None:
        api = MagicMock()
        mock_gc.return_value = api
        comment_obj = MagicMock()
        comment_obj.id = "c1"
        comment_obj.content = "Test comment"
        api.add_comment.return_value = comment_obj

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "comment", "t1", "Test", "comment"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["ok"] is True
        assert data["data"]["comment_id"] == "c1"
        api.add_comment.assert_called_once_with(content="Test comment", task_id="t1")

    @patch("td.cli.comments.get_client")
    def test_list_comments(self, mock_gc: MagicMock) -> None:
        api = MagicMock()
        mock_gc.return_value = api
        c1 = MagicMock()
        c1.id = "c1"
        c1.content = "First"
        c1.posted_at = "2026-03-25"
        c1.to_dict.return_value = {"id": "c1", "content": "First", "posted_at": "2026-03-25"}
        api.get_comments.return_value = iter([[c1]])

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "comments", "t1"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["type"] == "comment_list"
        assert len(data["data"]) == 1


class TestRateLimitMonitor:
    def test_hook_captures_headers(self) -> None:
        import httpx

        from td.core.rate_limit import RateLimitMonitor

        monitor = RateLimitMonitor()
        request = httpx.Request("GET", "https://api.todoist.com/rest/v2/tasks")
        response = httpx.Response(
            200,
            request=request,
            headers={
                "X-Ratelimit-Remaining": "400",
                "X-Ratelimit-Limit": "450",
            },
        )

        monitor.hook(response)

        assert monitor.remaining == 400
        assert monitor.limit == 450

    @patch("td.cli.rate_limit.load_rate_limit_cache")
    def test_rate_limit_command(self, mock_cache: MagicMock) -> None:
        mock_cache.return_value = {"remaining": 380, "limit": 450}

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "rate-limit"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["data"]["remaining"] == 380
        assert data["data"]["limit"] == 450

    @patch("td.cli.rate_limit.load_rate_limit_cache")
    def test_rate_limit_no_data(self, mock_cache: MagicMock) -> None:
        mock_cache.return_value = {"remaining": None, "limit": None}

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "rate-limit"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["type"] == "success"


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
        import httpx

        api = MagicMock()
        mock_gc.return_value = api
        request = httpx.Request("POST", "https://api.todoist.com/rest/v2/tasks/bad/close")
        response = httpx.Response(404, request=request)
        api.complete_task.side_effect = httpx.HTTPStatusError(
            "404 Not Found", request=request, response=response
        )

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
