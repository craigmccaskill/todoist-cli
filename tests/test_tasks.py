"""Tests for task commands and core business logic."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from td.cli import cli
from td.core.tasks import (
    _collect,
    complete_task,
    create_task,
    edit_task,
    list_tasks,
    quick_add,
    remove_task,
)


def _mock_task(**overrides: object) -> MagicMock:
    """Create a mock Task."""
    task = MagicMock()
    task.id = overrides.get("id", "t1")
    task.content = overrides.get("content", "Buy milk")
    task.priority = overrides.get("priority", 1)
    task.labels = overrides.get("labels", [])
    task.project_id = overrides.get("project_id", "p1")
    task.description = overrides.get("description", "")
    task.due = None
    task.to_dict.return_value = {
        "id": task.id,
        "content": task.content,
        "priority": task.priority,
        "labels": task.labels,
        "due": None,
    }
    return task


def _mock_project(**overrides: object) -> MagicMock:
    proj = MagicMock()
    proj.id = overrides.get("id", "p1")
    proj.name = overrides.get("name", "Inbox")
    proj.is_inbox_project = overrides.get("is_inbox_project", True)
    return proj


class TestCollect:
    def test_flattens_pages(self) -> None:
        pages = iter([[1, 2], [3, 4], [5]])  # type: ignore[list-item]
        result = _collect(pages)  # type: ignore[arg-type]
        assert result == [1, 2, 3, 4, 5]

    def test_empty_iterator(self) -> None:
        result = _collect(iter([]))  # type: ignore[arg-type]
        assert result == []


class TestCreateTask:
    def test_creates_task(self) -> None:
        api = MagicMock()
        expected = _mock_task()
        api.add_task.return_value = expected

        task, created = create_task(api, "Buy milk")
        assert created is True
        assert task == expected
        api.add_task.assert_called_once()

    def test_creates_with_options(self) -> None:
        api = MagicMock()
        api.add_task.return_value = _mock_task()

        create_task(
            api,
            "Review PR",
            project_id="p1",
            priority=4,
            due_string="tomorrow",
            labels=["work"],
        )
        _, kwargs = api.add_task.call_args
        assert kwargs["project_id"] == "p1"
        assert kwargs["priority"] == 4
        assert kwargs["due_string"] == "tomorrow"

    def test_idempotent_returns_existing(self) -> None:
        api = MagicMock()
        existing = _mock_task(content="Buy milk")
        api.get_tasks.return_value = iter([[existing]])

        task, created = create_task(api, "Buy milk", idempotent=True)
        assert created is False
        assert task == existing
        api.add_task.assert_not_called()

    def test_idempotent_creates_when_no_match(self) -> None:
        api = MagicMock()
        api.get_tasks.return_value = iter([[_mock_task(content="Something else")]])
        new_task = _mock_task(content="Buy milk")
        api.add_task.return_value = new_task

        _, created = create_task(api, "Buy milk", idempotent=True)
        assert created is True


class TestListTasks:
    def test_list_all(self) -> None:
        api = MagicMock()
        api.get_tasks.return_value = iter([[_mock_task(), _mock_task()]])
        result = list_tasks(api)
        assert len(result) == 2

    def test_filter_query(self) -> None:
        api = MagicMock()
        api.filter_tasks.return_value = iter([[_mock_task()]])
        result = list_tasks(api, filter_query="today & #Work")
        assert len(result) == 1
        api.filter_tasks.assert_called_once_with(query="today & #Work")


class TestCompleteTask:
    def test_completes(self) -> None:
        api = MagicMock()
        assert complete_task(api, "t1") is True
        api.complete_task.assert_called_once_with("t1")


class TestEditTask:
    def test_updates_fields(self) -> None:
        api = MagicMock()
        api.update_task.return_value = _mock_task()

        edit_task(api, "t1", content="Updated", priority=4)
        _, kwargs = api.update_task.call_args
        assert kwargs["content"] == "Updated"
        assert kwargs["priority"] == 4


class TestRemoveTask:
    def test_deletes(self) -> None:
        api = MagicMock()
        assert remove_task(api, "t1") is True
        api.delete_task.assert_called_once_with("t1")


class TestQuickAdd:
    def test_delegates_to_sdk(self) -> None:
        api = MagicMock()
        api.add_task_quick.return_value = _mock_task()
        quick_add(api, "Buy milk tomorrow p1 #Errands")
        api.add_task_quick.assert_called_once_with("Buy milk tomorrow p1 #Errands")


class TestCliCommands:
    """Integration tests for Click commands using CliRunner."""

    @patch("td.cli.tasks.get_client")
    def test_add_command(self, mock_gc: MagicMock) -> None:
        api = MagicMock()
        mock_gc.return_value = api
        task = _mock_task(content="Test task")
        api.add_task.return_value = task

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "add", "Test", "task"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["ok"] is True
        assert data["data"]["created"] is True

    @patch("td.cli.tasks.get_client")
    def test_ls_command(self, mock_gc: MagicMock) -> None:
        api = MagicMock()
        mock_gc.return_value = api
        api.get_tasks.return_value = iter([[_mock_task(), _mock_task()]])

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "ls"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["type"] == "task_list"
        assert len(data["data"]) == 2

    @patch("td.cli.tasks.get_client")
    @patch("td.cli.tasks.get_inbox_project")
    def test_inbox_command(self, mock_inbox: MagicMock, mock_gc: MagicMock) -> None:
        api = MagicMock()
        mock_gc.return_value = api
        mock_inbox.return_value = _mock_project()
        api.get_tasks.return_value = iter([[_mock_task()]])

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "inbox"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["type"] == "task_list"

    @patch("td.cli.tasks.get_client")
    def test_done_command(self, mock_gc: MagicMock) -> None:
        api = MagicMock()
        mock_gc.return_value = api

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "done", "t1"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["ok"] is True

    @patch("td.cli.tasks.get_client")
    def test_delete_with_yes(self, mock_gc: MagicMock) -> None:
        api = MagicMock()
        mock_gc.return_value = api

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "delete", "t1", "-y"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["ok"] is True

    @patch("td.cli.tasks.get_client")
    def test_quick_command(self, mock_gc: MagicMock) -> None:
        api = MagicMock()
        mock_gc.return_value = api
        api.add_task_quick.return_value = _mock_task()

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "quick", "Buy", "milk", "tomorrow"])

        assert result.exit_code == 0
        api.add_task_quick.assert_called_once_with("Buy milk tomorrow")

    @patch("td.cli.tasks.get_client")
    def test_add_idempotent(self, mock_gc: MagicMock) -> None:
        api = MagicMock()
        mock_gc.return_value = api
        existing = _mock_task(content="Buy milk")
        api.get_tasks.return_value = iter([[existing]])

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "add", "Buy", "milk", "--idempotent"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["data"]["created"] is False
        api.add_task.assert_not_called()
