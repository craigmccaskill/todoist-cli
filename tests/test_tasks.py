"""Tests for task commands and core business logic."""

from __future__ import annotations

import json
import sys
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
    uncomplete_task,
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


class TestUncompleteTask:
    def test_uncompletes(self) -> None:
        api = MagicMock()
        assert uncomplete_task(api, "t1") is True
        api.uncomplete_task.assert_called_once_with("t1")


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
    def test_ls_default_today(self, mock_gc: MagicMock) -> None:
        api = MagicMock()
        mock_gc.return_value = api
        api.filter_tasks.return_value = iter([[_mock_task(), _mock_task()]])

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "ls"])

        assert result.exit_code == 0
        api.filter_tasks.assert_called_once_with(query="overdue | today")
        data = json.loads(result.output)
        assert data["type"] == "task_list"
        assert len(data["data"]) == 2

    @patch("td.cli.tasks.get_client")
    def test_ls_ids_flag(self, mock_gc: MagicMock) -> None:
        api = MagicMock()
        mock_gc.return_value = api
        api.filter_tasks.return_value = iter([[_mock_task(id="t1"), _mock_task(id="t2")]])

        runner = CliRunner()
        result = runner.invoke(cli, ["ls", "--ids"])

        assert result.exit_code == 0
        lines = result.output.strip().split("\n")
        assert lines == ["t1", "t2"]

    @patch("td.cli.tasks.get_client")
    def test_ls_all_flag(self, mock_gc: MagicMock) -> None:
        api = MagicMock()
        mock_gc.return_value = api
        api.get_tasks.return_value = iter([[_mock_task()]])

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "ls", "--all"])

        assert result.exit_code == 0
        api.get_tasks.assert_called_once()

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
    def test_tomorrow_command(self, mock_gc: MagicMock) -> None:
        api = MagicMock()
        mock_gc.return_value = api
        api.filter_tasks.return_value = iter([[_mock_task(content="Morning standup")]])

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "tomorrow"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["type"] == "task_list"
        api.filter_tasks.assert_called_once_with(query="tomorrow")

    @patch("td.cli.tasks.get_client")
    def test_upcoming_command_default(self, mock_gc: MagicMock) -> None:
        api = MagicMock()
        mock_gc.return_value = api
        api.filter_tasks.return_value = iter([[_mock_task()]])

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "upcoming"])

        assert result.exit_code == 0
        api.filter_tasks.assert_called_once_with(query="7 days")

    @patch("td.cli.tasks.get_client")
    def test_upcoming_custom_days(self, mock_gc: MagicMock) -> None:
        api = MagicMock()
        mock_gc.return_value = api
        api.filter_tasks.return_value = iter([[]])

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "upcoming", "3"])

        assert result.exit_code == 0
        api.filter_tasks.assert_called_once_with(query="3 days")

    @patch("td.cli.tasks.get_client")
    def test_overdue_command(self, mock_gc: MagicMock) -> None:
        api = MagicMock()
        mock_gc.return_value = api
        api.filter_tasks.return_value = iter([[_mock_task(content="Late task")]])

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "overdue"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["type"] == "task_list"
        api.filter_tasks.assert_called_once_with(query="overdue")

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
    def test_done_batch(self, mock_gc: MagicMock) -> None:
        api = MagicMock()
        mock_gc.return_value = api
        # Set up cache so row numbers resolve
        from td.core.cache import save_result_cache

        save_result_cache(["t1", "t2", "t3", "t4"])

        task2 = _mock_task(id="t2", content="Task two")
        task4 = _mock_task(id="t4", content="Task four")
        api.get_task.side_effect = lambda tid: {"t2": task2, "t4": task4}[tid]

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "done", "2", "4"])

        assert result.exit_code == 0
        assert api.complete_task.call_count == 2

    @patch("td.cli.tasks.get_client")
    def test_done_single_word_not_batch(self, mock_gc: MagicMock) -> None:
        """Single digit is single task, not batch."""
        api = MagicMock()
        mock_gc.return_value = api

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "done", "t1"])

        assert result.exit_code == 0
        api.complete_task.assert_called_once()

    @patch("td.cli.tasks.get_client")
    def test_done_multi_word_not_batch(self, mock_gc: MagicMock) -> None:
        """Multi-word text is content match, not batch."""
        api = MagicMock()
        mock_gc.return_value = api
        match = _mock_task(id="t1", content="buy milk")
        api.get_tasks.return_value = iter([[match]])

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "done", "buy", "milk"])

        assert result.exit_code == 0
        api.complete_task.assert_called_once()

    @patch("td.cli.tasks.get_client")
    def test_done_unresolvable_text_ref_errors_early(self, mock_gc: MagicMock) -> None:
        """Text ref with no fuzzy match should error, not hit the API."""
        api = MagicMock()
        mock_gc.return_value = api
        api.get_tasks.return_value = iter([[]])  # no matches

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "done", "ljasdf"])

        assert result.exit_code == 1
        assert "not found" in result.output.lower()
        api.complete_task.assert_not_called()

    @patch("td.cli.tasks.get_client")
    def test_done_short_ref_passes_through(self, mock_gc: MagicMock) -> None:
        """Short refs (<=2 chars) pass through as task IDs — no fuzzy match."""
        api = MagicMock()
        mock_gc.return_value = api

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "done", "t1"])

        assert result.exit_code == 0
        api.complete_task.assert_called_once()

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
    def test_quick_command_deprecated(self, mock_gc: MagicMock) -> None:
        api = MagicMock()
        mock_gc.return_value = api
        api.add_task_quick.return_value = _mock_task()

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "quick", "Buy", "milk", "tomorrow"])

        assert result.exit_code == 0
        api.add_task_quick.assert_called_once_with("Buy milk tomorrow")
        assert "td quick is now td add" in result.output

    @patch("td.cli.tasks.get_client")
    def test_search_command(self, mock_gc: MagicMock) -> None:
        api = MagicMock()
        mock_gc.return_value = api
        api.filter_tasks.return_value = iter(
            [[_mock_task(content="Deploy v2"), _mock_task(content="Deploy v3")]]
        )

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "search", "deploy"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["type"] == "task_list"
        assert len(data["data"]) == 2
        api.filter_tasks.assert_called_once_with(query="search: deploy")

    @patch("td.cli.tasks.get_client")
    def test_search_empty_query_rejected(self, mock_gc: MagicMock) -> None:
        api = MagicMock()
        mock_gc.return_value = api

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "search", ""])

        assert result.exit_code == 1
        data = json.loads(result.output, strict=False)
        assert data["error"]["code"] == "VALIDATION_ERROR"
        api.filter_tasks.assert_not_called()

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


class TestUnifiedAdd:
    """Tests for unified add command with NLP/literal mode switching."""

    @patch("td.cli.tasks.get_client")
    def test_non_tty_uses_literal_by_default(self, mock_gc: MagicMock) -> None:
        """CliRunner is non-TTY, so add should use add_task (literal)."""
        api = MagicMock()
        mock_gc.return_value = api
        task = _mock_task(content="Deploy v2")
        api.add_task.return_value = task

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "add", "Deploy", "v2"])

        assert result.exit_code == 0
        api.add_task.assert_called_once()
        api.add_task_quick.assert_not_called()

    @patch("td.cli.tasks.get_client")
    @patch("td.cli.tasks.sys")
    def test_tty_uses_nlp_by_default(self, mock_sys: MagicMock, mock_gc: MagicMock) -> None:
        """In TTY mode with no flags, add should use quick_add (NLP)."""
        api = MagicMock()
        mock_gc.return_value = api
        api.add_task_quick.return_value = _mock_task(content="buy milk tomorrow")
        mock_sys.stdin.isatty.return_value = True
        mock_sys.stdout = sys.stdout
        mock_sys.stderr = sys.stderr

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "add", "buy", "milk", "tomorrow"])

        assert result.exit_code == 0
        api.add_task_quick.assert_called_once_with("buy milk tomorrow")
        api.add_task.assert_not_called()

    @patch("td.cli.tasks.get_client")
    def test_literal_flag_forces_add_task(self, mock_gc: MagicMock) -> None:
        """--literal should always use add_task even in TTY."""
        api = MagicMock()
        mock_gc.return_value = api
        api.add_task.return_value = _mock_task(content="buy milk")

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "add", "--literal", "buy", "milk"])

        assert result.exit_code == 0
        api.add_task.assert_called_once()
        api.add_task_quick.assert_not_called()

    @patch("td.cli.tasks.get_client")
    def test_nlp_flag_forces_quick_add(self, mock_gc: MagicMock) -> None:
        """--nlp should always use quick_add even in non-TTY."""
        api = MagicMock()
        mock_gc.return_value = api
        api.add_task_quick.return_value = _mock_task(content="buy milk tomorrow")

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "add", "--nlp", "buy", "milk", "tomorrow"])

        assert result.exit_code == 0
        api.add_task_quick.assert_called_once_with("buy milk tomorrow")
        api.add_task.assert_not_called()

    @patch("td.cli.tasks.get_client")
    @patch("td.cli.tasks.sys")
    def test_explicit_flags_override_tty_nlp(
        self, mock_sys: MagicMock, mock_gc: MagicMock
    ) -> None:
        """Explicit flags (--project, --due, etc.) force literal even in TTY."""
        api = MagicMock()
        mock_gc.return_value = api
        mock_sys.stdin.isatty.return_value = True
        mock_sys.stdout = sys.stdout
        mock_sys.stderr = sys.stderr

        proj = MagicMock()
        proj.id = "p1"
        proj.name = "Work"
        api.get_projects.return_value = iter([[proj]])
        api.add_task.return_value = _mock_task(content="Deploy v2")

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "add", "Deploy", "v2", "-p", "Work"])

        assert result.exit_code == 0
        api.add_task.assert_called_once()
        api.add_task_quick.assert_not_called()

    @patch("td.cli.tasks.get_client")
    def test_pipe_stdin_uses_literal(self, mock_gc: MagicMock) -> None:
        """Piped stdin should use literal mode."""
        api = MagicMock()
        mock_gc.return_value = api
        api.add_task.return_value = _mock_task(content="buy milk")

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "add"], input="buy milk\n")

        assert result.exit_code == 0
        api.add_task.assert_called_once()
        api.add_task_quick.assert_not_called()

    @patch("td.cli.tasks.get_client")
    def test_nlp_with_flags_warns_and_uses_literal(self, mock_gc: MagicMock) -> None:
        """--nlp with structured flags should warn and fall back to literal."""
        api = MagicMock()
        mock_gc.return_value = api
        api.add_task.return_value = _mock_task(content="buy milk")

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "add", "--nlp", "buy", "milk", "--due", "tomorrow"])

        assert result.exit_code == 0
        assert "--nlp ignored" in result.output
        # Flags override --nlp, so add_task is used
        api.add_task.assert_called_once()
        api.add_task_quick.assert_not_called()
