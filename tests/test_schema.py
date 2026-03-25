"""Tests for schema generation."""

from __future__ import annotations

import json

from click.testing import CliRunner

from td.cli import cli


class TestSchemaCommand:
    def test_outputs_valid_json(self) -> None:
        runner = CliRunner()
        result = runner.invoke(cli, ["schema"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["name"] == "td"
        assert "version" in data
        assert "commands" in data

    def test_contains_all_commands(self) -> None:
        runner = CliRunner()
        result = runner.invoke(cli, ["schema"])
        data = json.loads(result.output)

        expected = {
            "add",
            "capture",
            "comment",
            "comments",
            "ls",
            "done",
            "edit",
            "delete",
            "inbox",
            "today",
            "next",
            "log",
            "focus",
            "move",
            "quick",
            "search",
            "show",
            "undo",
            "project-add",
            "projects",
            "sections",
            "section-add",
            "labels",
            "label-add",
            "init",
            "completions",
            "schema",
        }
        assert set(data["commands"].keys()) == expected

    def test_command_has_description(self) -> None:
        runner = CliRunner()
        result = runner.invoke(cli, ["schema"])
        data = json.loads(result.output)

        assert data["commands"]["add"]["description"]
        assert data["commands"]["ls"]["description"]

    def test_command_has_options(self) -> None:
        runner = CliRunner()
        result = runner.invoke(cli, ["schema"])
        data = json.loads(result.output)

        add_cmd = data["commands"]["add"]
        option_names = [o["name"] for o in add_cmd["options"]]
        assert "project_name" in option_names
        assert "priority" in option_names
        assert "idempotent" in option_names

    def test_arguments_listed(self) -> None:
        runner = CliRunner()
        result = runner.invoke(cli, ["schema"])
        data = json.loads(result.output)

        done_cmd = data["commands"]["done"]
        arg_names = [a["name"] for a in done_cmd["arguments"]]
        assert "task_ref" in arg_names
