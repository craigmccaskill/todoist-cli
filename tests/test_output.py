"""Tests for the output formatting system."""

from __future__ import annotations

import json
from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock

from td.cli.output import (
    OutputFormatter,
    OutputMode,
    _empty_message,
    _format_timestamp,
    _is_overdue,
    resolve_output_mode,
)


def _make_task(**overrides: object) -> MagicMock:
    """Create a mock Task with sensible defaults."""
    task = MagicMock()
    task.id = overrides.get("id", "123456")
    task.content = overrides.get("content", "Buy milk")
    task.priority = overrides.get("priority", 1)
    task.labels = overrides.get("labels", [])
    task.project_id = overrides.get("project_id", "proj1")
    task.description = overrides.get("description", "")

    due = overrides.get("due")
    if due is None:
        task.due = None
    else:
        task.due = MagicMock()
        task.due.date = due
        task.due.string = due

    task.to_dict.return_value = {
        "id": task.id,
        "content": task.content,
        "priority": task.priority,
        "labels": task.labels,
        "due": {"date": due, "string": due} if due else None,
    }
    return task


def _make_project(**overrides: object) -> MagicMock:
    proj = MagicMock()
    proj.id = overrides.get("id", "proj1")
    proj.name = overrides.get("name", "Work")
    proj.is_favorite = overrides.get("is_favorite", False)
    proj.to_dict.return_value = {
        "id": proj.id,
        "name": proj.name,
        "is_favorite": proj.is_favorite,
    }
    return proj


def _make_label(**overrides: object) -> MagicMock:
    label = MagicMock()
    label.id = overrides.get("id", "label1")
    label.name = overrides.get("name", "urgent")
    label.to_dict.return_value = {"id": label.id, "name": label.name}
    return label


def _make_section(**overrides: object) -> MagicMock:
    sec = MagicMock()
    sec.id = overrides.get("id", "sec1")
    sec.name = overrides.get("name", "In Progress")
    sec.to_dict.return_value = {"id": sec.id, "name": sec.name}
    return sec


def _make_comment(**overrides: object) -> MagicMock:
    comment = MagicMock()
    comment.id = overrides.get("id", "comment1")
    comment.content = overrides.get("content", "Looking good!")
    comment.posted_at = overrides.get("posted_at", "2026-04-01T12:00:00Z")
    comment.to_dict.return_value = {
        "id": comment.id,
        "content": comment.content,
        "posted_at": comment.posted_at,
    }
    return comment


class TestResolveOutputMode:
    def test_json_flag(self) -> None:
        assert resolve_output_mode(True, False) == OutputMode.JSON

    def test_plain_flag(self) -> None:
        assert resolve_output_mode(False, True) == OutputMode.PLAIN

    def test_no_color(self) -> None:
        assert resolve_output_mode(False, False, color=False) == OutputMode.PLAIN

    def test_tty_default(self, monkeypatch: object) -> None:
        # When running in pytest, stdout is not a TTY
        # so this will resolve to JSON
        mode = resolve_output_mode(False, False, color=True)
        assert mode in (OutputMode.RICH, OutputMode.JSON)

    def test_default_format_json(self) -> None:
        mode = resolve_output_mode(False, False, default_format="json")
        assert mode == OutputMode.JSON

    def test_default_format_plain(self) -> None:
        mode = resolve_output_mode(False, False, default_format="plain")
        assert mode == OutputMode.PLAIN

    def test_default_format_rich(self) -> None:
        mode = resolve_output_mode(False, False, default_format="rich")
        assert mode == OutputMode.RICH

    def test_flag_overrides_default_format(self) -> None:
        mode = resolve_output_mode(True, False, default_format="plain")
        assert mode == OutputMode.JSON

    def test_default_format_case_insensitive(self) -> None:
        mode = resolve_output_mode(False, False, default_format="JSON")
        assert mode == OutputMode.JSON

    def test_invalid_default_format_ignored(self) -> None:
        # Falls through to TTY detection
        mode = resolve_output_mode(False, False, default_format="invalid")
        assert mode in (OutputMode.RICH, OutputMode.JSON)


class TestHelpers:
    def test_is_overdue_past_date(self) -> None:
        assert _is_overdue("2020-01-01") is True

    def test_is_overdue_future_date(self) -> None:
        assert _is_overdue("2099-12-31") is False

    def test_is_overdue_invalid_date(self) -> None:
        assert _is_overdue("not-a-date") is False

    def test_format_timestamp_minutes_ago(self) -> None:
        now = datetime.now(tz=timezone.utc)
        recent = (now - timedelta(minutes=5)).isoformat()
        result = _format_timestamp(recent)
        assert result.endswith("m ago")

    def test_format_timestamp_hours_ago(self) -> None:
        now = datetime.now(tz=timezone.utc)
        hours_ago = (now - timedelta(hours=3)).isoformat()
        result = _format_timestamp(hours_ago)
        assert result.endswith("h ago")

    def test_format_timestamp_days_ago(self) -> None:
        now = datetime.now(tz=timezone.utc)
        days_ago = (now - timedelta(days=3)).isoformat()
        result = _format_timestamp(days_ago)
        assert result.endswith("d ago")

    def test_format_timestamp_old_date(self) -> None:
        result = _format_timestamp("2025-01-15T12:00:00+00:00")
        assert "Jan" in result and "15" in result

    def test_format_timestamp_invalid(self) -> None:
        result = _format_timestamp("not-a-timestamp")
        assert result == "not-a-timestamp"

    def test_empty_message_tasks(self) -> None:
        assert _empty_message("tasks") == "No tasks found."

    def test_empty_message_projects(self) -> None:
        assert _empty_message("projects") == "No projects found."

    def test_empty_message_unknown(self) -> None:
        assert _empty_message("widgets") == "No widgets found."


class TestJsonOutput:
    def test_task_list_json(self, capsys: object) -> None:
        fmt = OutputFormatter(OutputMode.JSON)
        tasks = [_make_task(content="Task 1"), _make_task(content="Task 2")]
        fmt.task_list(tasks)

        captured = capsys.readouterr()  # type: ignore[union-attr]
        data = json.loads(captured.out)
        assert data["ok"] is True
        assert data["type"] == "task_list"
        assert len(data["data"]) == 2

    def test_single_task_json(self, capsys: object) -> None:
        fmt = OutputFormatter(OutputMode.JSON)
        task = _make_task(content="Buy milk", priority=4)
        fmt.task(task)

        captured = capsys.readouterr()  # type: ignore[union-attr]
        data = json.loads(captured.out)
        assert data["ok"] is True
        assert data["type"] == "task"

    def test_project_list_json(self, capsys: object) -> None:
        fmt = OutputFormatter(OutputMode.JSON)
        projects = [_make_project(name="Work"), _make_project(name="Personal")]
        fmt.project_list(projects)

        captured = capsys.readouterr()  # type: ignore[union-attr]
        data = json.loads(captured.out)
        assert data["type"] == "project_list"
        assert len(data["data"]) == 2

    def test_label_list_json(self, capsys: object) -> None:
        fmt = OutputFormatter(OutputMode.JSON)
        labels = [_make_label(name="urgent")]
        fmt.label_list(labels)

        captured = capsys.readouterr()  # type: ignore[union-attr]
        data = json.loads(captured.out)
        assert data["type"] == "label_list"

    def test_section_list_json(self, capsys: object) -> None:
        fmt = OutputFormatter(OutputMode.JSON)
        sections = [_make_section(name="Backlog")]
        fmt.section_list(sections)

        captured = capsys.readouterr()  # type: ignore[union-attr]
        data = json.loads(captured.out)
        assert data["type"] == "section_list"

    def test_success_json(self, capsys: object) -> None:
        fmt = OutputFormatter(OutputMode.JSON)
        fmt.success("Done!", {"task_id": "123"})

        captured = capsys.readouterr()  # type: ignore[union-attr]
        data = json.loads(captured.out)
        assert data["ok"] is True
        assert data["type"] == "success"

    def test_item_created_json(self, capsys: object) -> None:
        fmt = OutputFormatter(OutputMode.JSON)
        task = _make_task(content="New task")
        fmt.item_created("task", task, created=True)

        captured = capsys.readouterr()  # type: ignore[union-attr]
        data = json.loads(captured.out)
        assert data["data"]["created"] is True

    def test_item_already_exists_json(self, capsys: object) -> None:
        fmt = OutputFormatter(OutputMode.JSON)
        task = _make_task(content="Existing task")
        fmt.item_created("task", task, created=False)

        captured = capsys.readouterr()  # type: ignore[union-attr]
        data = json.loads(captured.out)
        assert data["data"]["created"] is False

    def test_comment_list_json(self, capsys: object) -> None:
        fmt = OutputFormatter(OutputMode.JSON)
        comments = [_make_comment(content="Great work")]
        fmt.comment_list(comments)

        captured = capsys.readouterr()  # type: ignore[union-attr]
        data = json.loads(captured.out)
        assert data["type"] == "comment_list"
        assert len(data["data"]) == 1

    def test_empty_task_list_json(self, capsys: object) -> None:
        fmt = OutputFormatter(OutputMode.JSON)
        fmt.task_list([])

        captured = capsys.readouterr()  # type: ignore[union-attr]
        data = json.loads(captured.out)
        assert data["ok"] is True
        assert data["data"] == []

    def test_empty_project_list_json(self, capsys: object) -> None:
        fmt = OutputFormatter(OutputMode.JSON)
        fmt.project_list([])

        captured = capsys.readouterr()  # type: ignore[union-attr]
        data = json.loads(captured.out)
        assert data["data"] == []

    def test_empty_comment_list_json(self, capsys: object) -> None:
        fmt = OutputFormatter(OutputMode.JSON)
        fmt.comment_list([])

        captured = capsys.readouterr()  # type: ignore[union-attr]
        data = json.loads(captured.out)
        assert data["data"] == []


class TestPlainOutput:
    def test_task_list_plain(self, capsys: object) -> None:
        fmt = OutputFormatter(OutputMode.PLAIN)
        tasks = [
            _make_task(content="Buy milk", due="2026-03-25", labels=["errands"]),
            _make_task(content="Code review", priority=4),
        ]
        pnames = {"proj1": "Work"}
        fmt.task_list(tasks, project_names=pnames)

        captured = capsys.readouterr()  # type: ignore[union-attr]
        lines = captured.out.strip().split("\n")
        assert lines[0] == "#\tPRI\tCONTENT\tPROJECT\tDUE\tLABELS"
        assert "Buy milk" in lines[1]
        assert "\t" in lines[1]

    def test_task_list_plain_no_project(self, capsys: object) -> None:
        fmt = OutputFormatter(OutputMode.PLAIN)
        tasks = [_make_task(content="Buy milk")]
        fmt.task_list(tasks, show_project=False)

        captured = capsys.readouterr()  # type: ignore[union-attr]
        lines = captured.out.strip().split("\n")
        assert "PROJECT" not in lines[0]

    def test_task_list_plain_no_labels(self, capsys: object) -> None:
        fmt = OutputFormatter(OutputMode.PLAIN)
        tasks = [_make_task(content="Buy milk")]
        fmt.task_list(tasks, show_labels=False)

        captured = capsys.readouterr()  # type: ignore[union-attr]
        lines = captured.out.strip().split("\n")
        assert "LABELS" not in lines[0]

    def test_task_list_plain_smart_hide_labels(self, capsys: object) -> None:
        """When no tasks have labels, LABELS column is auto-hidden."""
        fmt = OutputFormatter(OutputMode.PLAIN)
        tasks = [_make_task(content="No labels", labels=[])]
        fmt.task_list(tasks)

        captured = capsys.readouterr()  # type: ignore[union-attr]
        lines = captured.out.strip().split("\n")
        assert "LABELS" not in lines[0]

    def test_project_list_plain(self, capsys: object) -> None:
        fmt = OutputFormatter(OutputMode.PLAIN)
        fmt.project_list([_make_project(name="Work", is_favorite=True)])

        captured = capsys.readouterr()  # type: ignore[union-attr]
        lines = captured.out.strip().split("\n")
        assert lines[0] == "NAME\t\u2605\tID"
        assert "Work" in lines[1]
        assert "*" in lines[1]

    def test_project_list_plain_no_favorite(self, capsys: object) -> None:
        fmt = OutputFormatter(OutputMode.PLAIN)
        fmt.project_list([_make_project(name="Work", is_favorite=False)])

        captured = capsys.readouterr()  # type: ignore[union-attr]
        lines = captured.out.strip().split("\n")
        assert "Work" in lines[1]

    def test_label_list_plain_at_prefix(self, capsys: object) -> None:
        fmt = OutputFormatter(OutputMode.PLAIN)
        fmt.label_list([_make_label(name="urgent")])

        captured = capsys.readouterr()  # type: ignore[union-attr]
        lines = captured.out.strip().split("\n")
        assert lines[0] == "NAME\tID"
        assert "@urgent" in lines[1]

    def test_section_list_plain_name_first(self, capsys: object) -> None:
        fmt = OutputFormatter(OutputMode.PLAIN)
        fmt.section_list([_make_section(name="In Progress", id="sec1")])

        captured = capsys.readouterr()  # type: ignore[union-attr]
        lines = captured.out.strip().split("\n")
        assert lines[0] == "NAME\tID"
        assert lines[1].startswith("In Progress")

    def test_comment_list_plain(self, capsys: object) -> None:
        fmt = OutputFormatter(OutputMode.PLAIN)
        fmt.comment_list([_make_comment(content="Nice!", posted_at="2026-04-01T12:00:00Z")])

        captured = capsys.readouterr()  # type: ignore[union-attr]
        lines = captured.out.strip().split("\n")
        assert lines[0] == "CONTENT\tPOSTED\tID"
        assert "Nice!" in lines[1]

    def test_success_plain(self, capsys: object) -> None:
        fmt = OutputFormatter(OutputMode.PLAIN)
        fmt.success("Task completed")

        captured = capsys.readouterr()  # type: ignore[union-attr]
        assert captured.out.strip() == "Task completed"

    def test_empty_task_list_plain(self, capsys: object) -> None:
        fmt = OutputFormatter(OutputMode.PLAIN)
        fmt.task_list([])

        captured = capsys.readouterr()  # type: ignore[union-attr]
        assert captured.out.strip() == "No tasks found."

    def test_empty_project_list_plain(self, capsys: object) -> None:
        fmt = OutputFormatter(OutputMode.PLAIN)
        fmt.project_list([])

        captured = capsys.readouterr()  # type: ignore[union-attr]
        assert captured.out.strip() == "No projects found."

    def test_empty_label_list_plain(self, capsys: object) -> None:
        fmt = OutputFormatter(OutputMode.PLAIN)
        fmt.label_list([])

        captured = capsys.readouterr()  # type: ignore[union-attr]
        assert captured.out.strip() == "No labels found."

    def test_empty_section_list_plain(self, capsys: object) -> None:
        fmt = OutputFormatter(OutputMode.PLAIN)
        fmt.section_list([])

        captured = capsys.readouterr()  # type: ignore[union-attr]
        assert captured.out.strip() == "No sections found."

    def test_empty_comment_list_plain(self, capsys: object) -> None:
        fmt = OutputFormatter(OutputMode.PLAIN)
        fmt.comment_list([])

        captured = capsys.readouterr()  # type: ignore[union-attr]
        assert captured.out.strip() == "No comments found."


class TestRichOutput:
    def test_task_list_renders(self, capsys: object) -> None:
        fmt = OutputFormatter(OutputMode.RICH)
        tasks = [_make_task(content="Buy milk", priority=4, labels=["errands"])]
        fmt.task_list(tasks)
        # Rich writes to its own console — just verify no exception

    def test_single_task_renders(self) -> None:
        fmt = OutputFormatter(OutputMode.RICH)
        task = _make_task(content="Review PR", priority=3, due="tomorrow", labels=["work"])
        # Should not raise
        fmt.task(task)

    def test_project_list_renders(self) -> None:
        fmt = OutputFormatter(OutputMode.RICH)
        fmt.project_list([_make_project()])

    def test_success_renders(self) -> None:
        fmt = OutputFormatter(OutputMode.RICH)
        fmt.success("All done!")

    def test_comment_list_renders(self) -> None:
        fmt = OutputFormatter(OutputMode.RICH)
        fmt.comment_list([_make_comment()])

    def test_empty_task_list_renders(self) -> None:
        fmt = OutputFormatter(OutputMode.RICH)
        fmt.task_list([])

    def test_empty_project_list_renders(self) -> None:
        fmt = OutputFormatter(OutputMode.RICH)
        fmt.project_list([])

    def test_empty_label_list_renders(self) -> None:
        fmt = OutputFormatter(OutputMode.RICH)
        fmt.label_list([])

    def test_empty_section_list_renders(self) -> None:
        fmt = OutputFormatter(OutputMode.RICH)
        fmt.section_list([])

    def test_empty_comment_list_renders(self) -> None:
        fmt = OutputFormatter(OutputMode.RICH)
        fmt.comment_list([])

    def test_overdue_task_renders(self) -> None:
        fmt = OutputFormatter(OutputMode.RICH)
        task = _make_task(content="Overdue task", priority=4, due="2020-01-01")
        # Should render without exception — overdue styling applied
        fmt.task(task)

    def test_overdue_task_list_renders(self) -> None:
        fmt = OutputFormatter(OutputMode.RICH)
        tasks = [_make_task(content="Overdue", due="2020-01-01")]
        fmt.task_list(tasks)
