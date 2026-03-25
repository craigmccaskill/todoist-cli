"""Tests for dynamic shell completions."""

from __future__ import annotations

from unittest.mock import MagicMock, patch

from td.cli.completions import _complete_labels, _complete_projects, _complete_sections


class TestProjectCompletions:
    @patch("td.core.cache.load_name_cache")
    def test_completes_from_cache(self, mock_cache: MagicMock) -> None:
        mock_cache.return_value = {
            "projects": [
                {"name": "Work"},
                {"name": "Personal"},
                {"name": "Side Projects"},
            ]
        }
        ctx = MagicMock()
        param = MagicMock()

        results = _complete_projects(ctx, param, "W")
        assert len(results) == 1
        assert results[0].value == "Work"

    @patch("td.core.cache.load_name_cache")
    def test_completes_case_insensitive(self, mock_cache: MagicMock) -> None:
        mock_cache.return_value = {"projects": [{"name": "Work"}, {"name": "Personal"}]}
        ctx = MagicMock()
        param = MagicMock()

        results = _complete_projects(ctx, param, "w")
        assert len(results) == 1
        assert results[0].value == "Work"

    @patch("td.core.cache.load_name_cache")
    def test_empty_incomplete_returns_all(self, mock_cache: MagicMock) -> None:
        mock_cache.return_value = {"projects": [{"name": "Work"}, {"name": "Personal"}]}
        ctx = MagicMock()
        param = MagicMock()

        results = _complete_projects(ctx, param, "")
        assert len(results) == 2

    @patch("td.core.cache.load_name_cache")
    def test_no_cache_returns_empty(self, mock_cache: MagicMock) -> None:
        mock_cache.side_effect = Exception("no cache")
        ctx = MagicMock()
        param = MagicMock()

        results = _complete_projects(ctx, param, "W")
        assert results == []


class TestLabelCompletions:
    @patch("td.core.cache.load_name_cache")
    def test_completes_labels(self, mock_cache: MagicMock) -> None:
        mock_cache.return_value = {
            "labels": [{"name": "urgent"}, {"name": "work"}, {"name": "errands"}]
        }
        ctx = MagicMock()
        param = MagicMock()

        results = _complete_labels(ctx, param, "u")
        assert len(results) == 1
        assert results[0].value == "urgent"


class TestSectionCompletions:
    @patch("td.core.cache.load_name_cache")
    def test_completes_sections(self, mock_cache: MagicMock) -> None:
        mock_cache.return_value = {
            "sections": [{"name": "Backlog"}, {"name": "In Progress"}, {"name": "Done"}]
        }
        ctx = MagicMock()
        param = MagicMock()

        results = _complete_sections(ctx, param, "In")
        assert len(results) == 1
        assert results[0].value == "In Progress"
