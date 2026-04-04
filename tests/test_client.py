"""Tests for API client construction."""

from __future__ import annotations

from pathlib import Path

import pytest

from td.core.client import get_client
from td.core.exceptions import AuthError


class TestGetClient:
    def test_raises_when_no_token(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        monkeypatch.setenv("TD_CONFIG_DIR", str(tmp_path))
        monkeypatch.delenv("TD_API_TOKEN", raising=False)

        with pytest.raises(AuthError, match="No API token configured"):
            get_client()

    def test_returns_client_with_env_token(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("TD_API_TOKEN", "test-token")

        client = get_client()
        assert client is not None

    def test_returns_client_with_config_token(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        monkeypatch.setenv("TD_CONFIG_DIR", str(tmp_path))
        monkeypatch.delenv("TD_API_TOKEN", raising=False)

        from td.core.config import TdConfig, save_config

        save_config(TdConfig(api_token="file-token"))

        client = get_client()
        assert client is not None
