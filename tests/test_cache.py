"""Tests for result cache and name cache."""

from __future__ import annotations

from pathlib import Path

import pytest

from td.core.cache import (
    atomic_write,
    load_name_cache,
    load_result_cache,
    resolve_task_ref,
    save_name_cache,
    save_result_cache,
)


class TestResultCache:
    def test_save_and_load(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path))
        save_result_cache(["aaa", "bbb", "ccc"])
        cache = load_result_cache()
        assert cache["1"] == "aaa"
        assert cache["2"] == "bbb"
        assert cache["3"] == "ccc"

    def test_empty_when_missing(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path))
        assert load_result_cache() == {}

    def test_stale_cache_returns_empty(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path))
        save_result_cache(["aaa"])
        assert load_result_cache(max_age=0) == {}


class TestResolveTaskRef:
    def test_resolves_row_number(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path))
        save_result_cache(["task-abc", "task-def"])
        assert resolve_task_ref("1") == "task-abc"
        assert resolve_task_ref("2") == "task-def"

    def test_passes_through_task_id(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path))
        assert resolve_task_ref("abc123") == "abc123"

    def test_uncached_number_passes_through(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path))
        # No cache saved
        assert resolve_task_ref("5") == "5"


class TestNameCache:
    def test_save_and_load_projects(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path))
        save_name_cache(projects=[{"id": "p1", "name": "Work"}])
        cache = load_name_cache()
        assert cache["projects"][0]["name"] == "Work"

    def test_stale_returns_empty(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path))
        save_name_cache(projects=[{"id": "p1", "name": "Work"}])
        assert load_name_cache(max_age=0) == {}

    def test_merges_updates(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        monkeypatch.setenv("XDG_CACHE_HOME", str(tmp_path))
        save_name_cache(projects=[{"id": "p1", "name": "Work"}])
        save_name_cache(labels=[{"id": "l1", "name": "urgent"}])
        cache = load_name_cache()
        assert "projects" in cache
        assert "labels" in cache


class TestAtomicWrite:
    def test_writes_file_contents(self, tmp_path: Path) -> None:
        target = tmp_path / "test.json"
        atomic_write(target, '{"key": "value"}')
        assert target.read_text() == '{"key": "value"}'

    def test_no_temp_files_left(self, tmp_path: Path) -> None:
        target = tmp_path / "test.json"
        atomic_write(target, "data")
        files = list(tmp_path.iterdir())
        assert files == [target]

    def test_original_intact_on_failure(self, tmp_path: Path) -> None:
        target = tmp_path / "test.json"
        target.write_text("original")

        # Make the directory read-only so rename fails after mkstemp
        import os
        import stat

        # Create a subdirectory for isolation
        sub = tmp_path / "sub"
        sub.mkdir()
        target2 = sub / "test.json"
        target2.write_text("original")

        # Write to a non-existent directory to trigger failure
        bad_path = tmp_path / "nonexistent" / "test.json"
        with pytest.raises(OSError):
            atomic_write(bad_path, "new data")

        # Original file untouched
        assert target2.read_text() == "original"

    def test_overwrites_existing(self, tmp_path: Path) -> None:
        target = tmp_path / "test.json"
        target.write_text("old")
        atomic_write(target, "new")
        assert target.read_text() == "new"
