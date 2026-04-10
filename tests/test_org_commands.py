"""Tests for organization commands (projects, sections, labels, comments)."""

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
    sec.project_id = overrides.get("project_id", "p1")
    sec.to_dict.return_value = {"id": sec.id, "name": sec.name, "project_id": sec.project_id}
    return sec


def _mock_label(**overrides: object) -> MagicMock:
    lbl = MagicMock()
    lbl.id = overrides.get("id", "lbl1")
    lbl.name = overrides.get("name", "urgent")
    lbl.to_dict.return_value = {"id": lbl.id, "name": lbl.name}
    return lbl


def _mock_comment(**overrides: object) -> MagicMock:
    cmt = MagicMock()
    cmt.id = overrides.get("id", "c1")
    cmt.content = overrides.get("content", "A comment")
    cmt.posted_at = overrides.get("posted_at", "2026-04-09T12:00:00Z")
    cmt.to_dict.return_value = {
        "id": cmt.id,
        "content": cmt.content,
        "posted_at": cmt.posted_at,
    }
    return cmt


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


class TestProjectAddCommand:
    @patch("td.cli.projects.get_client")
    def test_creates_project(self, mock_gc: MagicMock) -> None:
        api = MagicMock()
        mock_gc.return_value = api
        proj = _mock_project(name="New Project", id="p99")
        api.add_project.return_value = proj

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "project-add", "New", "Project"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["ok"] is True
        assert data["data"]["name"] == "New Project"
        api.add_project.assert_called_once()

    @patch("td.cli.projects.get_client")
    def test_creates_with_parent(self, mock_gc: MagicMock) -> None:
        api = MagicMock()
        mock_gc.return_value = api
        parent = _mock_project(name="Work", id="p1")
        api.get_projects.return_value = iter([[parent]])
        child = _mock_project(name="Sub Project", id="p99")
        api.add_project.return_value = child

        runner = CliRunner()
        result = runner.invoke(
            cli, ["--json", "project-add", "Sub", "Project", "--parent", "Work"]
        )

        assert result.exit_code == 0
        _, kwargs = api.add_project.call_args
        assert kwargs["parent_id"] == "p1"

    @patch("td.cli.projects.get_client")
    def test_creates_favorite(self, mock_gc: MagicMock) -> None:
        api = MagicMock()
        mock_gc.return_value = api
        api.add_project.return_value = _mock_project(name="Fav", is_favorite=True)

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "project-add", "Fav", "--favorite"])

        assert result.exit_code == 0
        _, kwargs = api.add_project.call_args
        assert kwargs["is_favorite"] is True


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

    @patch("td.cli.sections.get_client")
    def test_lists_all_sections_grouped_by_project(self, mock_gc: MagicMock) -> None:
        api = MagicMock()
        mock_gc.return_value = api
        api.get_sections.return_value = iter(
            [
                [
                    _mock_section(name="Backlog", project_id="p1"),
                    _mock_section(name="Done", id="s2", project_id="p1"),
                    _mock_section(name="Ideas", id="s3", project_id="p2"),
                ]
            ]
        )
        api.get_projects.return_value = iter(
            [[_mock_project(name="Work", id="p1"), _mock_project(name="Personal", id="p2")]]
        )

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "sections"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["type"] == "section_list_grouped"
        assert len(data["data"]) == 2
        assert data["data"][0]["project_name"] == "Work"
        assert len(data["data"][0]["sections"]) == 2
        assert data["data"][1]["project_name"] == "Personal"

    @patch("td.cli.sections.get_client")
    def test_no_sections_shows_empty(self, mock_gc: MagicMock) -> None:
        api = MagicMock()
        mock_gc.return_value = api
        api.get_sections.return_value = iter([[]])

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "sections"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["type"] == "section_list"
        assert data["data"] == []


class TestSectionAddCommand:
    @patch("td.cli.sections.get_client")
    def test_creates_section(self, mock_gc: MagicMock) -> None:
        api = MagicMock()
        mock_gc.return_value = api
        api.get_projects.return_value = iter([[_mock_project(name="Work", id="p1")]])
        api.add_section.return_value = _mock_section(name="In Progress")

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "section-add", "In", "Progress", "-p", "Work"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["ok"] is True
        assert data["data"]["name"] == "In Progress"
        api.add_section.assert_called_once_with(name="In Progress", project_id="p1")

    @patch("td.cli.sections.get_client")
    def test_section_add_requires_project(self, mock_gc: MagicMock) -> None:
        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "section-add", "Test"])

        assert result.exit_code != 0
        assert "project" in result.output.lower() or "required" in result.output.lower()


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
    def test_creates_label(self, mock_gc: MagicMock) -> None:
        api = MagicMock()
        mock_gc.return_value = api
        api.add_label.return_value = _mock_label(name="important")

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "label-add", "important"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["ok"] is True
        assert data["data"]["name"] == "important"
        api.add_label.assert_called_once_with(name="important")

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


# --- Project edit/delete/archive/unarchive ---


class TestProjectEditCommand:
    @patch("td.cli.projects.get_client")
    def test_renames_project(self, mock_gc: MagicMock) -> None:
        api = MagicMock()
        mock_gc.return_value = api
        proj = _mock_project(name="Work", id="p1")
        api.get_projects.return_value = iter([[proj]])
        updated = _mock_project(name="Work stuff", id="p1")
        api.update_project.return_value = updated

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "project-edit", "Work", "--name", "Work stuff"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["ok"] is True
        assert data["data"]["name"] == "Work stuff"
        api.update_project.assert_called_once_with("p1", name="Work stuff", color=None)

    @patch("td.cli.projects.get_client")
    def test_recolors_project(self, mock_gc: MagicMock) -> None:
        api = MagicMock()
        mock_gc.return_value = api
        proj = _mock_project(name="Work", id="p1")
        api.get_projects.return_value = iter([[proj]])
        updated = _mock_project(name="Work", id="p1")
        api.update_project.return_value = updated

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "project-edit", "Work", "--color", "blue"])

        assert result.exit_code == 0
        api.update_project.assert_called_once_with("p1", name=None, color="blue")

    @patch("td.cli.projects.get_client")
    def test_edit_no_flags_errors(self, mock_gc: MagicMock) -> None:
        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "project-edit", "Work"])

        assert result.exit_code == 1


class TestProjectDeleteCommand:
    @patch("td.cli.projects.get_client")
    def test_deletes_with_yes(self, mock_gc: MagicMock) -> None:
        api = MagicMock()
        mock_gc.return_value = api
        proj = _mock_project(name="Old", id="p1")
        api.get_projects.return_value = iter([[proj]])

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "project-delete", "Old", "-y"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["ok"] is True
        api.delete_project.assert_called_once_with("p1")

    @patch("td.cli.projects.get_client")
    def test_delete_confirms_in_tty(self, mock_gc: MagicMock) -> None:
        api = MagicMock()
        mock_gc.return_value = api
        proj = _mock_project(name="Old", id="p1")
        api.get_projects.return_value = iter([[proj]])

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "project-delete", "Old"], input="y\n")

        assert result.exit_code == 0
        api.delete_project.assert_called_once_with("p1")

    @patch("td.cli.projects.get_client")
    def test_delete_aborts_on_no(self, mock_gc: MagicMock) -> None:
        api = MagicMock()
        mock_gc.return_value = api
        proj = _mock_project(name="Old", id="p1")
        api.get_projects.return_value = iter([[proj]])

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "project-delete", "Old"], input="n\n")

        assert result.exit_code == 0
        api.delete_project.assert_not_called()

    @patch("td.cli.projects.get_client")
    def test_delete_not_found(self, mock_gc: MagicMock) -> None:
        api = MagicMock()
        mock_gc.return_value = api
        api.get_projects.return_value = iter([[]])

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "project-delete", "Nonexistent", "-y"])

        assert result.exit_code == 1


class TestProjectArchiveCommand:
    @patch("td.cli.projects.get_client")
    def test_archives_project(self, mock_gc: MagicMock) -> None:
        api = MagicMock()
        mock_gc.return_value = api
        proj = _mock_project(name="Work", id="p1")
        api.get_projects.return_value = iter([[proj]])

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "project-archive", "Work"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["ok"] is True
        api.archive_project.assert_called_once_with("p1")


class TestProjectUnarchiveCommand:
    @patch("td.cli.projects.get_client")
    def test_unarchives_project(self, mock_gc: MagicMock) -> None:
        api = MagicMock()
        mock_gc.return_value = api
        proj = _mock_project(name="Work", id="p1")
        api.get_projects.return_value = iter([[proj]])

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "project-unarchive", "Work"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["ok"] is True
        api.unarchive_project.assert_called_once_with("p1")


# --- Section edit/delete ---


class TestSectionEditCommand:
    @patch("td.cli.sections.get_client")
    def test_renames_section(self, mock_gc: MagicMock) -> None:
        api = MagicMock()
        mock_gc.return_value = api
        proj = _mock_project(name="Work", id="p1")
        api.get_projects.return_value = iter([[proj]])
        sec = _mock_section(name="Backlog", id="s1", project_id="p1")
        api.get_sections.return_value = iter([[sec]])
        updated = _mock_section(name="Active", id="s1")
        api.update_section.return_value = updated

        runner = CliRunner()
        result = runner.invoke(
            cli, ["--json", "section-edit", "Backlog", "--name", "Active", "-p", "Work"]
        )

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["ok"] is True
        assert data["data"]["name"] == "Active"
        api.update_section.assert_called_once_with("s1", name="Active")

    @patch("td.cli.sections.get_client")
    def test_renames_section_without_project(self, mock_gc: MagicMock) -> None:
        api = MagicMock()
        mock_gc.return_value = api
        sec = _mock_section(name="Backlog", id="s1")
        api.get_sections.return_value = iter([[sec]])
        updated = _mock_section(name="Active", id="s1")
        api.update_section.return_value = updated

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "section-edit", "Backlog", "--name", "Active"])

        assert result.exit_code == 0
        api.update_section.assert_called_once_with("s1", name="Active")


class TestSectionDeleteCommand:
    @patch("td.cli.sections.get_client")
    def test_deletes_with_yes(self, mock_gc: MagicMock) -> None:
        api = MagicMock()
        mock_gc.return_value = api
        sec = _mock_section(name="Old", id="s1")
        api.get_sections.return_value = iter([[sec]])

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "section-delete", "Old", "-y"])

        assert result.exit_code == 0
        api.delete_section.assert_called_once_with("s1")

    @patch("td.cli.sections.get_client")
    def test_delete_confirms_in_tty(self, mock_gc: MagicMock) -> None:
        api = MagicMock()
        mock_gc.return_value = api
        sec = _mock_section(name="Old", id="s1")
        api.get_sections.return_value = iter([[sec]])

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "section-delete", "Old"], input="y\n")

        assert result.exit_code == 0
        api.delete_section.assert_called_once_with("s1")

    @patch("td.cli.sections.get_client")
    def test_delete_aborts_on_no(self, mock_gc: MagicMock) -> None:
        api = MagicMock()
        mock_gc.return_value = api
        sec = _mock_section(name="Old", id="s1")
        api.get_sections.return_value = iter([[sec]])

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "section-delete", "Old"], input="n\n")

        assert result.exit_code == 0
        api.delete_section.assert_not_called()

    @patch("td.cli.sections.get_client")
    def test_delete_not_found(self, mock_gc: MagicMock) -> None:
        api = MagicMock()
        mock_gc.return_value = api
        api.get_sections.return_value = iter([[]])

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "section-delete", "Nonexistent", "-y"])

        assert result.exit_code == 1


# --- Label edit/delete ---


class TestLabelEditCommand:
    @patch("td.cli.labels.get_client")
    def test_renames_label(self, mock_gc: MagicMock) -> None:
        api = MagicMock()
        mock_gc.return_value = api
        lbl = _mock_label(name="urgent", id="lbl1")
        api.get_labels.return_value = iter([[lbl]])
        updated = _mock_label(name="critical", id="lbl1")
        api.update_label.return_value = updated

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "label-edit", "urgent", "--name", "critical"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["ok"] is True
        assert data["data"]["name"] == "critical"
        api.update_label.assert_called_once_with("lbl1", name="critical", color=None)

    @patch("td.cli.labels.get_client")
    def test_recolors_label(self, mock_gc: MagicMock) -> None:
        api = MagicMock()
        mock_gc.return_value = api
        lbl = _mock_label(name="urgent", id="lbl1")
        api.get_labels.return_value = iter([[lbl]])
        updated = _mock_label(name="urgent", id="lbl1")
        api.update_label.return_value = updated

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "label-edit", "urgent", "--color", "red"])

        assert result.exit_code == 0
        api.update_label.assert_called_once_with("lbl1", name=None, color="red")

    @patch("td.cli.labels.get_client")
    def test_edit_no_flags_errors(self, mock_gc: MagicMock) -> None:
        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "label-edit", "urgent"])

        assert result.exit_code == 1


class TestLabelDeleteCommand:
    @patch("td.cli.labels.get_client")
    def test_deletes_with_yes(self, mock_gc: MagicMock) -> None:
        api = MagicMock()
        mock_gc.return_value = api
        lbl = _mock_label(name="old", id="lbl1")
        api.get_labels.return_value = iter([[lbl]])

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "label-delete", "old", "-y"])

        assert result.exit_code == 0
        api.delete_label.assert_called_once_with("lbl1")

    @patch("td.cli.labels.get_client")
    def test_delete_confirms_in_tty(self, mock_gc: MagicMock) -> None:
        api = MagicMock()
        mock_gc.return_value = api
        lbl = _mock_label(name="old", id="lbl1")
        api.get_labels.return_value = iter([[lbl]])

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "label-delete", "old"], input="y\n")

        assert result.exit_code == 0
        api.delete_label.assert_called_once_with("lbl1")

    @patch("td.cli.labels.get_client")
    def test_delete_aborts_on_no(self, mock_gc: MagicMock) -> None:
        api = MagicMock()
        mock_gc.return_value = api
        lbl = _mock_label(name="old", id="lbl1")
        api.get_labels.return_value = iter([[lbl]])

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "label-delete", "old"], input="n\n")

        assert result.exit_code == 0
        api.delete_label.assert_not_called()

    @patch("td.cli.labels.get_client")
    def test_delete_not_found(self, mock_gc: MagicMock) -> None:
        api = MagicMock()
        mock_gc.return_value = api
        api.get_labels.return_value = iter([[]])

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "label-delete", "nonexistent", "-y"])

        assert result.exit_code == 1


# --- Comment edit/delete ---


class TestCommentEditCommand:
    @patch("td.cli.comments.get_client")
    def test_edits_comment_positional(self, mock_gc: MagicMock) -> None:
        api = MagicMock()
        mock_gc.return_value = api
        updated = _mock_comment(id="c1", content="Updated text")
        api.update_comment.return_value = updated

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "comment-edit", "c1", "Updated", "text"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["ok"] is True
        assert data["data"]["content"] == "Updated text"
        api.update_comment.assert_called_once_with("c1", content="Updated text")

    @patch("td.cli.comments.get_client")
    def test_edits_comment_flag(self, mock_gc: MagicMock) -> None:
        api = MagicMock()
        mock_gc.return_value = api
        updated = _mock_comment(id="c1", content="New content")
        api.update_comment.return_value = updated

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "comment-edit", "c1", "--content", "New content"])

        assert result.exit_code == 0
        api.update_comment.assert_called_once_with("c1", content="New content")

    @patch("td.cli.comments.get_client")
    def test_edit_no_content_errors(self, mock_gc: MagicMock) -> None:
        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "comment-edit", "c1"])

        assert result.exit_code == 1


class TestCommentDeleteCommand:
    @patch("td.cli.comments.get_client")
    def test_deletes_with_yes(self, mock_gc: MagicMock) -> None:
        api = MagicMock()
        mock_gc.return_value = api

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "comment-delete", "c1", "-y"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["ok"] is True
        api.delete_comment.assert_called_once_with("c1")

    @patch("td.cli.comments.get_client")
    def test_delete_confirms_in_tty(self, mock_gc: MagicMock) -> None:
        api = MagicMock()
        mock_gc.return_value = api

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "comment-delete", "c1"], input="y\n")

        assert result.exit_code == 0
        api.delete_comment.assert_called_once_with("c1")

    @patch("td.cli.comments.get_client")
    def test_delete_aborts_on_no(self, mock_gc: MagicMock) -> None:
        api = MagicMock()
        mock_gc.return_value = api

        runner = CliRunner()
        result = runner.invoke(cli, ["--json", "comment-delete", "c1"], input="n\n")

        assert result.exit_code == 0
        api.delete_comment.assert_not_called()
