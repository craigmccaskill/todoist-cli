"""Tests for config loading, saving, and path resolution."""

from __future__ import annotations

from pathlib import Path

import pytest

from td.core.config import (
    TdConfig,
    get_config_dir,
    get_config_path,
    load_config,
    resolve_token,
    save_config,
)


class TestGetConfigDir:
    def test_default_xdg(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        monkeypatch.delenv("TD_CONFIG_DIR", raising=False)
        monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
        monkeypatch.setattr(Path, "home", staticmethod(lambda: tmp_path))
        assert get_config_dir() == tmp_path / ".config" / "td"

    def test_xdg_override(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        monkeypatch.delenv("TD_CONFIG_DIR", raising=False)
        monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "custom"))
        assert get_config_dir() == tmp_path / "custom" / "td"

    def test_td_config_dir_override(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        monkeypatch.setenv("TD_CONFIG_DIR", str(tmp_path / "myconfig"))
        assert get_config_dir() == tmp_path / "myconfig"


class TestSaveAndLoadConfig:
    def test_round_trip(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        monkeypatch.setenv("TD_CONFIG_DIR", str(tmp_path))
        monkeypatch.delenv("TD_API_TOKEN", raising=False)
        monkeypatch.delenv("NO_COLOR", raising=False)

        config = TdConfig(api_token="test-token-123", default_project="Work")
        save_config(config)

        assert (tmp_path / "config.toml").exists()

        loaded = load_config()
        assert loaded.api_token == "test-token-123"
        assert loaded.default_project == "Work"
        assert loaded.color is True

    def test_creates_parent_dirs(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        deep_path = tmp_path / "a" / "b" / "c"
        monkeypatch.setenv("TD_CONFIG_DIR", str(deep_path))

        save_config(TdConfig(api_token="tok"))
        assert (deep_path / "config.toml").exists()

    def test_no_color_env(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        monkeypatch.setenv("TD_CONFIG_DIR", str(tmp_path))
        monkeypatch.delenv("TD_API_TOKEN", raising=False)
        monkeypatch.setenv("NO_COLOR", "1")

        save_config(TdConfig(api_token="tok"))
        loaded = load_config()
        assert loaded.color is False

    def test_td_format_env(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        monkeypatch.setenv("TD_CONFIG_DIR", str(tmp_path))
        monkeypatch.delenv("TD_API_TOKEN", raising=False)
        monkeypatch.setenv("TD_FORMAT", "json")

        save_config(TdConfig(api_token="tok"))
        loaded = load_config()
        assert loaded.default_format == "json"

    def test_td_format_env_overrides_config(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        monkeypatch.setenv("TD_CONFIG_DIR", str(tmp_path))
        monkeypatch.delenv("TD_API_TOKEN", raising=False)
        monkeypatch.setenv("TD_FORMAT", "json")

        save_config(TdConfig(api_token="tok", default_format="plain"))
        loaded = load_config()
        assert loaded.default_format == "json"


class TestResolveToken:
    def test_env_var_precedence(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        monkeypatch.setenv("TD_CONFIG_DIR", str(tmp_path))
        monkeypatch.setenv("TD_API_TOKEN", "env-token")

        save_config(TdConfig(api_token="file-token"))
        assert resolve_token() == "env-token"

    def test_falls_back_to_file(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        monkeypatch.setenv("TD_CONFIG_DIR", str(tmp_path))
        monkeypatch.delenv("TD_API_TOKEN", raising=False)

        save_config(TdConfig(api_token="file-token"))
        assert resolve_token() == "file-token"

    def test_none_when_missing(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        monkeypatch.setenv("TD_CONFIG_DIR", str(tmp_path))
        monkeypatch.delenv("TD_API_TOKEN", raising=False)
        assert resolve_token() is None


class TestGetConfigPath:
    def test_returns_toml_path(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        monkeypatch.setenv("TD_CONFIG_DIR", str(tmp_path))
        assert get_config_path() == tmp_path / "config.toml"
