"""Tests for name-to-ID resolution in core modules."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

import pytest

from td.core.exceptions import (
    LabelNotFoundError,
    ProjectNotFoundError,
    SectionNotFoundError,
)
from td.core.labels import resolve_label
from td.core.projects import get_inbox_project, resolve_project
from td.core.sections import resolve_section


def _mock_project(**overrides: object) -> MagicMock:
    proj = MagicMock()
    proj.id = overrides.get("id", "p1")
    proj.name = overrides.get("name", "Work")
    proj.is_inbox_project = overrides.get("is_inbox_project", False)
    return proj


def _mock_label(**overrides: object) -> MagicMock:
    lbl = MagicMock()
    lbl.id = overrides.get("id", "lbl1")
    lbl.name = overrides.get("name", "urgent")
    return lbl


def _mock_section(**overrides: object) -> MagicMock:
    sec = MagicMock()
    sec.id = overrides.get("id", "s1")
    sec.name = overrides.get("name", "Backlog")
    return sec


class TestResolveProject:
    def test_resolve_by_id(self) -> None:
        api = MagicMock()
        proj = _mock_project(id="p1", name="Work")
        api.get_projects.return_value = iter([[proj]])

        result = resolve_project(api, "p1")
        assert result.id == "p1"

    def test_resolve_by_name_case_insensitive(self) -> None:
        api = MagicMock()
        proj = _mock_project(id="p1", name="Work")
        api.get_projects.return_value = iter([[proj]])

        result = resolve_project(api, "work")
        assert result.id == "p1"

    def test_not_found_raises_with_suggestion(self) -> None:
        api = MagicMock()
        proj = _mock_project(id="p1", name="Work")
        api.get_projects.return_value = iter([[proj]])

        with pytest.raises(ProjectNotFoundError) as exc_info:
            resolve_project(api, "Wor")
        assert "Did you mean" in exc_info.value.suggestion
        assert "Work" in exc_info.value.suggestion

    def test_not_found_no_partial_match(self) -> None:
        api = MagicMock()
        proj = _mock_project(id="p1", name="Work")
        api.get_projects.return_value = iter([[proj]])

        with pytest.raises(ProjectNotFoundError):
            resolve_project(api, "zzz")


class TestGetInboxProject:
    def test_finds_inbox_by_flag(self) -> None:
        api = MagicMock()
        inbox = _mock_project(id="p1", name="Inbox", is_inbox_project=True)
        api.get_projects.return_value = iter([[inbox]])

        result = get_inbox_project(api)
        assert result.id == "p1"

    def test_finds_inbox_by_name_fallback(self) -> None:
        api = MagicMock()
        proj = _mock_project(id="p1", name="Inbox", is_inbox_project=False)
        api.get_projects.return_value = iter([[proj]])

        result = get_inbox_project(api)
        assert result.name == "Inbox"

    def test_raises_when_no_inbox(self) -> None:
        api = MagicMock()
        proj = _mock_project(id="p1", name="Work", is_inbox_project=False)
        api.get_projects.return_value = iter([[proj]])

        with pytest.raises(ProjectNotFoundError):
            get_inbox_project(api)


class TestResolveLabel:
    def test_resolve_by_id(self) -> None:
        api = MagicMock()
        lbl = _mock_label(id="lbl1", name="urgent")
        api.get_labels.return_value = iter([[lbl]])

        result = resolve_label(api, "lbl1")
        assert result.id == "lbl1"

    def test_resolve_by_name(self) -> None:
        api = MagicMock()
        lbl = _mock_label(id="lbl1", name="urgent")
        api.get_labels.return_value = iter([[lbl]])

        result = resolve_label(api, "Urgent")
        assert result.name == "urgent"

    def test_not_found_raises(self) -> None:
        api = MagicMock()
        api.get_labels.return_value = iter([[]])

        with pytest.raises(LabelNotFoundError, match="not found"):
            resolve_label(api, "missing")


class TestResolveSection:
    def test_resolve_by_id(self) -> None:
        api = MagicMock()
        sec = _mock_section(id="s1", name="Backlog")
        api.get_sections.return_value = iter([[sec]])

        result = resolve_section(api, "s1")
        assert result.id == "s1"

    def test_resolve_by_name(self) -> None:
        api = MagicMock()
        sec = _mock_section(id="s1", name="Backlog")
        api.get_sections.return_value = iter([[sec]])

        result = resolve_section(api, "backlog")
        assert result.name == "Backlog"

    def test_not_found_raises(self) -> None:
        api = MagicMock()
        api.get_sections.return_value = iter([[]])

        with pytest.raises(SectionNotFoundError, match="not found"):
            resolve_section(api, "missing")

    def test_filters_by_project_id(self) -> None:
        api = MagicMock()
        sec = _mock_section(id="s1", name="Backlog")
        api.get_sections.return_value = iter([[sec]])

        resolve_section(api, "s1", project_id="p1")
        _, kwargs = api.get_sections.call_args
        assert kwargs["project_id"] == "p1"


class TestNarrowedExceptionCatches:
    """Unexpected exceptions in cache operations must propagate, not be swallowed."""

    @patch("td.core.projects.save_name_cache", side_effect=RuntimeError("unexpected"))
    def test_unexpected_exception_propagates_from_project_cache(
        self,
        _mock_save: MagicMock,
    ) -> None:
        api = MagicMock()
        proj = _mock_project(id="p1", name="Work")
        api.get_projects.return_value = iter([[proj]])

        with pytest.raises(RuntimeError, match="unexpected"):
            resolve_project(api, "p1")

    @patch("td.core.projects.load_name_cache", side_effect=AttributeError("bug"))
    def test_unexpected_exception_propagates_from_cache_read(
        self,
        _mock_load: MagicMock,
    ) -> None:
        api = MagicMock()
        proj = _mock_project(id="p1", name="Work")
        api.get_projects.return_value = iter([[proj]])

        with pytest.raises(AttributeError, match="bug"):
            resolve_project(api, "p1")
