"""Tests for the output formatting system."""

from __future__ import annotations

import json
from unittest.mock import MagicMock

from td.cli.output import OutputFormatter, OutputMode, resolve_output_mode


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


class TestPlainOutput:
    def test_task_list_plain(self, capsys: object) -> None:
        fmt = OutputFormatter(OutputMode.PLAIN)
        tasks = [
            _make_task(content="Buy milk", due="2026-03-25"),
            _make_task(content="Code review", priority=4),
        ]
        fmt.task_list(tasks)

        captured = capsys.readouterr()  # type: ignore[union-attr]
        lines = captured.out.strip().split("\n")
        assert lines[0] == "ID\tCONTENT\tDUE\tPRIORITY\tLABELS"
        assert "Buy milk" in lines[1]
        assert "\t" in lines[1]

    def test_project_list_plain(self, capsys: object) -> None:
        fmt = OutputFormatter(OutputMode.PLAIN)
        fmt.project_list([_make_project(name="Work")])

        captured = capsys.readouterr()  # type: ignore[union-attr]
        lines = captured.out.strip().split("\n")
        assert "Work" in lines[1]

    def test_success_plain(self, capsys: object) -> None:
        fmt = OutputFormatter(OutputMode.PLAIN)
        fmt.success("Task completed")

        captured = capsys.readouterr()  # type: ignore[union-attr]
        assert captured.out.strip() == "Task completed"


class TestRichOutput:
    def test_task_list_renders(self, capsys: object) -> None:
        fmt = OutputFormatter(OutputMode.RICH)
        tasks = [_make_task(content="Buy milk", priority=4, labels=["errands"])]
        fmt.task_list(tasks)
        # Rich writes to its own console — just verify no exception

    def test_single_task_renders(self) -> None:
        fmt = OutputFormatter(OutputMode.RICH)
        task = _make_task(
            content="Review PR", priority=3, due="tomorrow", labels=["work"]
        )
        # Should not raise
        fmt.task(task)

    def test_project_list_renders(self) -> None:
        fmt = OutputFormatter(OutputMode.RICH)
        fmt.project_list([_make_project()])

    def test_success_renders(self) -> None:
        fmt = OutputFormatter(OutputMode.RICH)
        fmt.success("All done!")
