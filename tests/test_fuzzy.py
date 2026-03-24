"""Tests for fuzzy content matching."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from td.cli import cli
from td.core.tasks import find_task_by_content


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


class TestFindTaskByContent:
    def test_exact_match(self) -> None:
        api = MagicMock()
        t1 = _mock_task(id="t1", content="Buy milk")
        t2 = _mock_task(id="t2", content="Buy milk and eggs")
        api.get_tasks.return_value = iter([[t1, t2]])

        result = find_task_by_content(api, "Buy milk")
        assert len(result) == 1
        assert result[0].id == "t1"

    def test_starts_with_match(self) -> None:
        api = MagicMock()
        t1 = _mock_task(id="t1", content="Review PR for auth")
        t2 = _mock_task(id="t2", content="Buy groceries")
        api.get_tasks.return_value = iter([[t1, t2]])

        result = find_task_by_content(api, "Review")
        assert len(result) == 1
        assert result[0].id == "t1"

    def test_contains_match(self) -> None:
        api = MagicMock()
        t1 = _mock_task(id="t1", content="Review PR for auth module")
        api.get_tasks.return_value = iter([[t1]])

        result = find_task_by_content(api, "auth")
        assert len(result) == 1

    def test_case_insensitive(self) -> None:
        api = MagicMock()
        t1 = _mock_task(id="t1", content="Buy Milk")
        api.get_tasks.return_value = iter([[t1]])

        result = find_task_by_content(api, "buy milk")
        assert len(result) == 1

    def test_no_match(self) -> None:
        api = MagicMock()
        t1 = _mock_task(id="t1", content="Buy milk")
        api.get_tasks.return_value = iter([[t1]])

        result = find_task_by_content(api, "dentist")
        assert len(result) == 0

    def test_multiple_matches(self) -> None:
        api = MagicMock()
        t1 = _mock_task(id="t1", content="Buy milk")
        t2 = _mock_task(id="t2", content="Buy eggs")
        api.get_tasks.return_value = iter([[t1, t2]])

        result = find_task_by_content(api, "Buy")
        assert len(result) == 2


class TestFuzzyCliIntegration:
    @patch("td.cli.tasks.get_client")
    def test_done_with_content_match(self, mock_gc: MagicMock) -> None:
        api = MagicMock()
        mock_gc.return_value = api
        t1 = _mock_task(id="t1", content="Buy milk")
        api.get_tasks.return_value = iter([[t1]])

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "done", "Buy milk"])

        assert result.exit_code == 0
        api.complete_task.assert_called_once_with("t1")

    @patch("td.cli.tasks.get_client")
    def test_done_with_partial_match(self, mock_gc: MagicMock) -> None:
        api = MagicMock()
        mock_gc.return_value = api
        t1 = _mock_task(id="t1", content="Buy milk and eggs")
        api.get_tasks.return_value = iter([[t1]])

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "done", "milk"])

        assert result.exit_code == 0
        api.complete_task.assert_called_once_with("t1")

    @patch("td.cli.tasks.get_client")
    def test_multiple_matches_non_interactive_errors(self, mock_gc: MagicMock) -> None:
        api = MagicMock()
        mock_gc.return_value = api
        t1 = _mock_task(id="t1", content="Buy milk")
        t2 = _mock_task(id="t2", content="Buy eggs")
        api.get_tasks.return_value = iter([[t1, t2]])

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "done", "Buy"])

        # Non-interactive: multiple matches should error
        assert result.exit_code == 1

    @patch("td.cli.tasks.get_client")
    def test_short_ref_passes_through(self, mock_gc: MagicMock) -> None:
        """Refs <= 2 chars skip fuzzy search (likely an ID or row number)."""
        api = MagicMock()
        mock_gc.return_value = api

        runner = CliRunner()
        runner.invoke(cli, ["--json", "done", "t1"])

        # Passes "t1" directly as task ID — no content search
        api.complete_task.assert_called_once_with("t1")
