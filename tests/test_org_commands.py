"""Tests for organization commands (projects, sections, labels)."""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from td.cli import cli


def _mock_project(**overrides: object) -> MagicMock:
    proj = MagicMock()
    proj.id = overrides.get("id", "p1")
    proj.name = overrides.get("name", "Work")
    proj.is_favorite = overrides.get("is_favorite", False)
    proj.is_inbox_project = overrides.get("is_inbox_project", False)
    proj.to_dict.return_value = {
        "id": proj.id,
        "name": proj.name,
        "is_favorite": proj.is_favorite,
    }
    return proj


def _mock_section(**overrides: object) -> MagicMock:
    sec = MagicMock()
    sec.id = overrides.get("id", "s1")
    sec.name = overrides.get("name", "In Progress")
    sec.to_dict.return_value = {"id": sec.id, "name": sec.name}
    return sec


def _mock_label(**overrides: object) -> MagicMock:
    lbl = MagicMock()
    lbl.id = overrides.get("id", "lbl1")
    lbl.name = overrides.get("name", "urgent")
    lbl.to_dict.return_value = {"id": lbl.id, "name": lbl.name}
    return lbl


class TestProjectsCommand:
    @patch("td.cli.projects.get_client")
    def test_lists_projects(self, mock_gc: MagicMock) -> None:
        api = MagicMock()
        mock_gc.return_value = api
        api.get_projects.return_value = iter(
            [[_mock_project(name="Work"), _mock_project(name="Personal")]]
        )

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "projects"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["type"] == "project_list"
        assert len(data["data"]) == 2

    @patch("td.cli.projects.get_client")
    def test_search_projects(self, mock_gc: MagicMock) -> None:
        api = MagicMock()
        mock_gc.return_value = api
        api.search_projects.return_value = iter([[_mock_project(name="Work")]])

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "projects", "-s", "Work"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert len(data["data"]) == 1


class TestSectionsCommand:
    @patch("td.cli.sections.get_client")
    def test_lists_sections(self, mock_gc: MagicMock) -> None:
        api = MagicMock()
        mock_gc.return_value = api
        # resolve_project needs projects
        api.get_projects.return_value = iter([[_mock_project(name="Work", id="p1")]])
        api.get_sections.return_value = iter(
            [[_mock_section(name="Backlog"), _mock_section(name="Done")]]
        )

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "sections", "-p", "Work"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["type"] == "section_list"
        assert len(data["data"]) == 2


class TestLabelsCommand:
    @patch("td.cli.labels.get_client")
    def test_lists_labels(self, mock_gc: MagicMock) -> None:
        api = MagicMock()
        mock_gc.return_value = api
        api.get_labels.return_value = iter([[_mock_label(name="urgent"), _mock_label(name="low")]])

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "labels"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["type"] == "label_list"
        assert len(data["data"]) == 2

    @patch("td.cli.labels.get_client")
    def test_search_labels(self, mock_gc: MagicMock) -> None:
        api = MagicMock()
        mock_gc.return_value = api
        api.search_labels.return_value = iter([[_mock_label(name="urgent")]])

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "labels", "-s", "urgent"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert len(data["data"]) == 1
