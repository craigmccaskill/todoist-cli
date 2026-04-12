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
            "comment",
            "comments",
            "completed",
            "doctor",
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
            "search",
            "show",
            "undo",
            "project",
            "projects",
            "section",
            "sections",
            "label",
            "labels",
            "tomorrow",
            "upcoming",
            "overdue",
            "rate-limit",
            "review",
            "init",
            "completions",
            "schema",
            "skill",
        }
        assert set(data["commands"].keys()) == expected

    def test_group_subcommands_in_schema(self) -> None:
        """Entity groups expose their verbs via a nested ``commands`` dict.

        ADR-0009 moved CRUD commands into entity groups; ADR-0006 requires
        the schema to describe the full surface. Agents walking the top
        level must see the verbs on each group without guessing flat
        name prefixes.
        """
        runner = CliRunner()
        result = runner.invoke(cli, ["schema"])
        data = json.loads(result.output)

        project = data["commands"]["project"]
        assert "commands" in project
        assert set(project["commands"].keys()) == {
            "add",
            "edit",
            "delete",
            "archive",
            "unarchive",
            "list",
        }

        section = data["commands"]["section"]
        assert set(section["commands"].keys()) == {"add", "edit", "delete", "list"}

        label = data["commands"]["label"]
        assert set(label["commands"].keys()) == {"add", "edit", "delete", "list"}

        comment = data["commands"]["comment"]
        assert set(comment["commands"].keys()) == {"add", "edit", "delete", "list"}

    def test_group_subcommand_carries_params(self) -> None:
        """Nested subcommand entries must carry the same shape (arguments, options)
        as leaf commands so agents can invoke them directly."""
        runner = CliRunner()
        result = runner.invoke(cli, ["schema"])
        data = json.loads(result.output)

        project_add = data["commands"]["project"]["commands"]["add"]
        assert "description" in project_add
        assert "arguments" in project_add
        assert "options" in project_add
        arg_names = [a["name"] for a in project_add["arguments"]]
        assert "name" in arg_names
        option_names = [o["name"] for o in project_add["options"]]
        assert "parent_name" in option_names

    def test_deprecated_aliases_hidden_from_schema(self) -> None:
        """The 13 hyphenated CRUD shims from v0.12.x are hidden in v0.13.0
        and must not appear in the schema. They are removed entirely in
        v0.14.0 per ADR-0009."""
        runner = CliRunner()
        result = runner.invoke(cli, ["schema"])
        data = json.loads(result.output)

        deprecated = {
            "project-add",
            "project-edit",
            "project-delete",
            "project-archive",
            "project-unarchive",
            "section-add",
            "section-edit",
            "section-delete",
            "label-add",
            "label-edit",
            "label-delete",
            "comment-edit",
            "comment-delete",
        }
        assert deprecated.isdisjoint(set(data["commands"].keys()))

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
