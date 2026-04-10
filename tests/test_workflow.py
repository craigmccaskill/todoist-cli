"""Tests for workflow commands and sorting."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from td.cli import cli
from td.core.tasks import sort_tasks


def _mock_task(**overrides: object) -> MagicMock:
    task = MagicMock()
    task.id = overrides.get("id", "t1")
    task.content = overrides.get("content", "Buy milk")
    task.priority = overrides.get("priority", 1)
    task.labels = overrides.get("labels", [])
    task.project_id = overrides.get("project_id", "p1")
    task.due = None
    if "due_date" in overrides:
        task.due = MagicMock()
        task.due.date = overrides["due_date"]
        task.due.string = overrides.get("due_string", overrides["due_date"])
    task.to_dict.return_value = {
        "id": task.id,
        "content": task.content,
        "priority": task.priority,
        "labels": task.labels,
        "due": {"date": task.due.date} if task.due else None,
    }
    return task


def _mock_project(**overrides: object) -> MagicMock:
    proj = MagicMock()
    proj.id = overrides.get("id", "p1")
    proj.name = overrides.get("name", "Work")
    proj.is_inbox_project = overrides.get("is_inbox_project", False)
    return proj


class TestSortTasks:
    def test_sort_by_priority(self) -> None:
        low = _mock_task(id="low", priority=1)
        high = _mock_task(id="high", priority=4)
        med = _mock_task(id="med", priority=3)

        result = sort_tasks([low, high, med], "priority")
        assert [t.id for t in result] == ["high", "med", "low"]

    def test_sort_by_due(self) -> None:
        later = _mock_task(id="later", due_date="2026-04-01")
        sooner = _mock_task(id="sooner", due_date="2026-03-25")
        no_date = _mock_task(id="nodate")

        result = sort_tasks([later, sooner, no_date], "due")
        assert [t.id for t in result] == ["sooner", "later", "nodate"]

    def test_sort_reverse(self) -> None:
        low = _mock_task(id="low", priority=1)
        high = _mock_task(id="high", priority=4)

        result = sort_tasks([low, high], "priority", reverse=True)
        assert [t.id for t in result] == ["low", "high"]

    def test_sort_no_date_last(self) -> None:
        with_date = _mock_task(id="dated", due_date="2026-03-25")
        without = _mock_task(id="undated")

        result = sort_tasks([without, with_date], "due")
        assert result[0].id == "dated"
        assert result[1].id == "undated"


class TestTodayCommand:
    @patch("td.cli.tasks.get_client")
    def test_today(self, mock_gc: MagicMock) -> None:
        api = MagicMock()
        mock_gc.return_value = api
        api.filter_tasks.return_value = iter([[_mock_task()]])

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "today"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["type"] == "task_list"
        api.filter_tasks.assert_called_once_with(query="overdue | today")


class TestNextCommand:
    @patch("td.cli.tasks.get_client")
    def test_next_returns_one_task(self, mock_gc: MagicMock) -> None:
        api = MagicMock()
        mock_gc.return_value = api
        low = _mock_task(id="low", priority=1)
        high = _mock_task(id="high", priority=4)
        api.filter_tasks.return_value = iter([[low, high]])

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "next"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["type"] == "task"
        assert data["data"]["id"] == "high"

    @patch("td.cli.tasks.get_client")
    def test_next_empty(self, mock_gc: MagicMock) -> None:
        api = MagicMock()
        mock_gc.return_value = api
        api.filter_tasks.return_value = iter([[]])

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "next"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["type"] == "success"

    @patch("td.cli.tasks.get_client")
    def test_next_with_project_filter(self, mock_gc: MagicMock) -> None:
        api = MagicMock()
        mock_gc.return_value = api
        t1 = _mock_task(id="t1", priority=4, project_id="p1")
        t2 = _mock_task(id="t2", priority=4, project_id="p2")
        api.filter_tasks.return_value = iter([[t1, t2]])
        proj = _mock_project(id="p1", name="Work")
        api.get_projects.return_value = iter([[proj]])

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "next", "-p", "Work"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["data"]["id"] == "t1"


class TestLogCommand:
    @patch("td.cli.tasks.get_client")
    def test_log_today(self, mock_gc: MagicMock) -> None:
        api = MagicMock()
        mock_gc.return_value = api
        api.get_completed_tasks_by_completion_date.return_value = iter(
            [[_mock_task(content="Done task")]]
        )

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "log"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["type"] == "task_list"

    @patch("td.cli.tasks.get_client")
    def test_log_week(self, mock_gc: MagicMock) -> None:
        api = MagicMock()
        mock_gc.return_value = api
        api.get_completed_tasks_by_completion_date.return_value = iter([[_mock_task()]])

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "log", "--week"])

        assert result.exit_code == 0


class TestCompletedCommand:
    @patch("td.cli.tasks.get_client")
    def test_completed_today_default(self, mock_gc: MagicMock) -> None:
        api = MagicMock()
        mock_gc.return_value = api
        api.get_completed_tasks_by_completion_date.return_value = iter(
            [[_mock_task(content="Done task", project_id="p1")]]
        )
        api.get_projects.return_value = iter([[_mock_project(id="p1", name="Work")]])

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "completed"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["type"] == "completed_list"
        assert len(data["data"]) == 1
        assert data["data"][0]["content"] == "Done task"

    @patch("td.cli.tasks.get_client")
    def test_completed_since_absolute(self, mock_gc: MagicMock) -> None:
        api = MagicMock()
        mock_gc.return_value = api
        api.get_completed_tasks_by_completion_date.return_value = iter(
            [[_mock_task(content="Old task")]]
        )
        api.get_projects.return_value = iter([[_mock_project()]])

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "completed", "--since", "2026-04-01"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["type"] == "completed_list"

    @patch("td.cli.tasks.get_client")
    def test_completed_since_relative(self, mock_gc: MagicMock) -> None:
        api = MagicMock()
        mock_gc.return_value = api
        api.get_completed_tasks_by_completion_date.return_value = iter(
            [[_mock_task(content="Recent task")]]
        )
        api.get_projects.return_value = iter([[_mock_project()]])

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "completed", "--since", "7 days"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["type"] == "completed_list"

    @patch("td.cli.tasks.get_client")
    def test_completed_project_positional(self, mock_gc: MagicMock) -> None:
        api = MagicMock()
        mock_gc.return_value = api
        task = _mock_task(content="Work task", project_id="p1")
        api.get_completed_tasks_by_completion_date.return_value = iter([[task]])
        proj = _mock_project(id="p1", name="Work")
        api.get_projects.return_value = iter([[proj]])

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "completed", "Work"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["type"] == "completed_list"

    @patch("td.cli.tasks.get_client")
    def test_completed_project_flag(self, mock_gc: MagicMock) -> None:
        api = MagicMock()
        mock_gc.return_value = api
        task = _mock_task(content="Work task", project_id="p1")
        api.get_completed_tasks_by_completion_date.return_value = iter([[task]])
        proj = _mock_project(id="p1", name="Work")
        api.get_projects.return_value = iter([[proj]])

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "completed", "-p", "Work"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["type"] == "completed_list"

    @patch("td.cli.tasks.get_client")
    def test_completed_empty(self, mock_gc: MagicMock) -> None:
        api = MagicMock()
        mock_gc.return_value = api
        api.get_completed_tasks_by_completion_date.return_value = iter([[]])
        api.get_projects.return_value = iter([[_mock_project()]])

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "completed"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["type"] == "completed_list"
        assert data["data"] == []

    @patch("td.cli.tasks.get_client")
    def test_completed_empty_plain(self, mock_gc: MagicMock) -> None:
        api = MagicMock()
        mock_gc.return_value = api
        api.get_completed_tasks_by_completion_date.return_value = iter([[]])
        api.get_projects.return_value = iter([[_mock_project()]])

        runner = CliRunner()
        result = runner.invoke(cli, ["--plain", "completed"])

        assert result.exit_code == 0
        assert "No tasks completed today." in result.output

    @patch("td.cli.tasks.get_client")
    def test_completed_invalid_since(self, mock_gc: MagicMock) -> None:
        api = MagicMock()
        mock_gc.return_value = api

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "completed", "--since", "garbage"])

        assert result.exit_code == 1

    # --- Positional duration args ---

    @patch("td.cli.tasks.get_client")
    def test_completed_duration_7d(self, mock_gc: MagicMock) -> None:
        api = MagicMock()
        mock_gc.return_value = api
        api.get_completed_tasks_by_completion_date.return_value = iter(
            [[_mock_task(content="Recent task")]]
        )
        api.get_projects.return_value = iter([[_mock_project()]])

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "completed", "7d"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["type"] == "completed_list"

    @patch("td.cli.tasks.get_client")
    def test_completed_duration_2w(self, mock_gc: MagicMock) -> None:
        api = MagicMock()
        mock_gc.return_value = api
        api.get_completed_tasks_by_completion_date.return_value = iter(
            [[_mock_task(content="Two week task")]]
        )
        api.get_projects.return_value = iter([[_mock_project()]])

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "completed", "2w"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["type"] == "completed_list"

    @patch("td.cli.tasks.get_client")
    def test_completed_duration_1m(self, mock_gc: MagicMock) -> None:
        api = MagicMock()
        mock_gc.return_value = api
        api.get_completed_tasks_by_completion_date.return_value = iter(
            [[_mock_task(content="Month old task")]]
        )
        api.get_projects.return_value = iter([[_mock_project()]])

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "completed", "1m"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["type"] == "completed_list"

    # --- Combined positional args ---

    @patch("td.cli.tasks.get_client")
    def test_completed_project_and_duration(self, mock_gc: MagicMock) -> None:
        """td completed Work 7d"""
        api = MagicMock()
        mock_gc.return_value = api
        task = _mock_task(content="Work task", project_id="p1")
        api.get_completed_tasks_by_completion_date.return_value = iter([[task]])
        proj = _mock_project(id="p1", name="Work")
        api.get_projects.return_value = iter([[proj]])

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "completed", "Work", "7d"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["type"] == "completed_list"

    @patch("td.cli.tasks.get_client")
    def test_completed_duration_and_project_reversed(self, mock_gc: MagicMock) -> None:
        """td completed 7d Work -- order doesn't matter"""
        api = MagicMock()
        mock_gc.return_value = api
        task = _mock_task(content="Work task", project_id="p1")
        api.get_completed_tasks_by_completion_date.return_value = iter([[task]])
        proj = _mock_project(id="p1", name="Work")
        api.get_projects.return_value = iter([[proj]])

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "completed", "7d", "Work"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["type"] == "completed_list"

    # --- Absolute date positional ---

    @patch("td.cli.tasks.get_client")
    def test_completed_absolute_date_positional(self, mock_gc: MagicMock) -> None:
        """td completed 2026-04-01"""
        api = MagicMock()
        mock_gc.return_value = api
        api.get_completed_tasks_by_completion_date.return_value = iter(
            [[_mock_task(content="Old task")]]
        )
        api.get_projects.return_value = iter([[_mock_project()]])

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "completed", "2026-04-01"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["type"] == "completed_list"

    # --- Flag overrides positional ---

    @patch("td.cli.tasks.get_client")
    def test_completed_flag_overrides_positional(self, mock_gc: MagicMock) -> None:
        """--since flag takes precedence over positional duration"""
        api = MagicMock()
        mock_gc.return_value = api
        api.get_completed_tasks_by_completion_date.return_value = iter(
            [[_mock_task(content="Task")]]
        )
        api.get_projects.return_value = iter([[_mock_project()]])

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "completed", "7d", "--since", "2026-04-01"])

        assert result.exit_code == 0

    # --- Error cases ---

    @patch("td.cli.tasks.get_client")
    def test_completed_duplicate_duration_error(self, mock_gc: MagicMock) -> None:
        """Two durations should error"""
        api = MagicMock()
        mock_gc.return_value = api

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "completed", "7d", "2w"])

        assert result.exit_code == 1

    @patch("td.cli.tasks.get_client")
    def test_completed_duplicate_project_error(self, mock_gc: MagicMock) -> None:
        """Two project names should error"""
        api = MagicMock()
        mock_gc.return_value = api

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "completed", "Work", "Personal"])

        assert result.exit_code == 1

    @patch("td.cli.tasks.get_client")
    def test_completed_invalid_positional_garbage(self, mock_gc: MagicMock) -> None:
        """Garbage that looks like a project gets passed to resolve_project"""
        api = MagicMock()
        mock_gc.return_value = api
        api.get_projects.return_value = iter([[]])

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "completed", "garbage"])

        # Should fail because "garbage" is treated as project name
        assert result.exit_code == 1


class TestFocusCommand:
    @patch("td.cli.tasks.get_client")
    def test_focus_project(self, mock_gc: MagicMock) -> None:
        api = MagicMock()
        mock_gc.return_value = api
        proj = _mock_project(id="p1", name="Work")
        api.get_projects.return_value = iter([[proj]])
        api.get_tasks.return_value = iter([[_mock_task(priority=4), _mock_task(priority=1)]])

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "focus", "Work"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["type"] == "task_list"


class TestDefaultCommand:
    @patch("td.cli.tasks.get_client")
    def test_no_subcommand_runs_today(self, mock_gc: MagicMock) -> None:
        api = MagicMock()
        mock_gc.return_value = api
        api.filter_tasks.return_value = iter([[_mock_task()]])
        api.get_projects.return_value = iter([[_mock_project()]])

        runner = CliRunner()
        result = runner.invoke(cli, ["--json"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["type"] == "task_list"
        api.filter_tasks.assert_called_once_with(query="overdue | today")


class TestLsSortFlag:
    @patch("td.cli.tasks.get_client")
    def test_ls_with_sort(self, mock_gc: MagicMock) -> None:
        api = MagicMock()
        mock_gc.return_value = api
        low = _mock_task(id="low", priority=1)
        high = _mock_task(id="high", priority=4)
        api.filter_tasks.return_value = iter([[low, high]])

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "ls", "--sort", "priority"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["data"][0]["id"] == "high"
