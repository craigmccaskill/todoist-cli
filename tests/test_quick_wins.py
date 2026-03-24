"""Tests for quick win features: capture, stdin, debug."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from td.cli import cli


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


class TestCapture:
    @patch("td.cli.tasks.get_client")
    def test_capture_to_inbox(self, mock_gc: MagicMock) -> None:
        api = MagicMock()
        mock_gc.return_value = api
        api.add_task.return_value = _mock_task(content="call dentist")

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "capture", "call", "dentist"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["ok"] is True


class TestStdinPiping:
    @patch("td.cli.tasks.get_client")
    def test_add_from_stdin(self, mock_gc: MagicMock) -> None:
        api = MagicMock()
        mock_gc.return_value = api
        api.add_task.return_value = _mock_task(content="piped task")

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "add"], input="piped task\n")

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["data"]["created"] is True

    @patch("td.cli.tasks.get_client")
    def test_quick_from_stdin(self, mock_gc: MagicMock) -> None:
        api = MagicMock()
        mock_gc.return_value = api
        api.add_task_quick.return_value = _mock_task()

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "quick"], input="Buy milk tomorrow\n")

        assert result.exit_code == 0


class TestDebugFlag:
    @patch("td.cli.tasks.get_client")
    def test_debug_flag_accepted(self, mock_gc: MagicMock) -> None:
        api = MagicMock()
        mock_gc.return_value = api
        api.filter_tasks.return_value = iter([[]])

        runner = CliRunner()
        result = runner.invoke(cli, ["--debug", "--json", "ls"])

        assert result.exit_code == 0
