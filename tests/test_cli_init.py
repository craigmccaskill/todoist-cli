"""Tests for td init and td completions commands."""

from __future__ import annotations

from pathlib import Path
from unittest.mock import MagicMock

import pytest
from click.testing import CliRunner

from td.cli import cli


class TestInit:
    def test_init_saves_token(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        monkeypatch.setenv("TD_CONFIG_DIR", str(tmp_path))
        monkeypatch.delenv("TD_API_TOKEN", raising=False)

        mock_api = MagicMock()
        mock_api.get_projects.return_value = iter(
            [
                [MagicMock(), MagicMock()],
            ]
        )

        monkeypatch.setattr("td.cli.config_cmd.TodoistAPI", lambda token: mock_api)

        runner = CliRunner()
        result = runner.invoke(cli, ["init"], input="test-token-123\n1\n")

        assert result.exit_code == 0
        assert "Authenticated" in result.output
        assert "Config saved" in result.output
        assert (tmp_path / "config.toml").exists()

    def test_init_aborts_on_invalid_token(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        monkeypatch.setenv("TD_CONFIG_DIR", str(tmp_path))
        monkeypatch.delenv("TD_API_TOKEN", raising=False)

        def bad_api(token: str) -> MagicMock:
            mock = MagicMock()
            mock.get_projects.side_effect = Exception("Unauthorized")
            return mock

        monkeypatch.setattr("td.cli.config_cmd.TodoistAPI", bad_api)

        runner = CliRunner()
        result = runner.invoke(cli, ["init"], input="bad-token\n")

        assert result.exit_code == 1
        assert not (tmp_path / "config.toml").exists()

    def test_init_asks_before_overwriting(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        monkeypatch.setenv("TD_CONFIG_DIR", str(tmp_path))
        monkeypatch.delenv("TD_API_TOKEN", raising=False)

        # Create existing config
        from td.core.config import TdConfig, save_config

        save_config(TdConfig(api_token="existing-token"))

        runner = CliRunner()
        # Answer 'n' to overwrite prompt
        result = runner.invoke(cli, ["init"], input="n\n")

        assert result.exit_code == 0
        assert "Aborted" in result.output

    def test_init_env_var_does_not_expose_token(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        monkeypatch.setenv("TD_CONFIG_DIR", str(tmp_path))
        monkeypatch.delenv("TD_API_TOKEN", raising=False)

        mock_api = MagicMock()
        mock_api.get_projects.return_value = iter(
            [
                [MagicMock(), MagicMock()],
            ]
        )

        monkeypatch.setattr("td.cli.config_cmd.TodoistAPI", lambda token: mock_api)

        runner = CliRunner()
        result = runner.invoke(cli, ["init"], input="secret-token-abc123\n2\n")

        assert result.exit_code == 0
        assert "secret-token-abc123" not in result.output
        assert "TD_API_TOKEN" in result.output

    def test_init_shows_trust_building_text(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        monkeypatch.setenv("TD_CONFIG_DIR", str(tmp_path))
        monkeypatch.delenv("TD_API_TOKEN", raising=False)

        mock_api = MagicMock()
        mock_api.get_projects.return_value = iter([[MagicMock()]])
        monkeypatch.setattr("td.cli.config_cmd.TodoistAPI", lambda token: mock_api)

        runner = CliRunner()
        result = runner.invoke(cli, ["init"], input="test-token\n1\n")

        assert result.exit_code == 0
        normalized = " ".join(result.output.split())
        assert "stored locally" in normalized
        assert "never sent anywhere except the Todoist API" in normalized

    def test_init_shows_todoist_url(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        monkeypatch.setenv("TD_CONFIG_DIR", str(tmp_path))
        monkeypatch.delenv("TD_API_TOKEN", raising=False)

        mock_api = MagicMock()
        mock_api.get_projects.return_value = iter([[MagicMock()]])
        monkeypatch.setattr("td.cli.config_cmd.TodoistAPI", lambda token: mock_api)

        runner = CliRunner()
        result = runner.invoke(cli, ["init"], input="test-token\n1\n")

        assert result.exit_code == 0
        assert "Todoist Settings" in result.output

    def test_init_bad_token_shows_specific_error(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        monkeypatch.setenv("TD_CONFIG_DIR", str(tmp_path))
        monkeypatch.delenv("TD_API_TOKEN", raising=False)

        from httpx import HTTPStatusError, Request, Response

        def bad_api(token: str) -> MagicMock:
            mock = MagicMock()
            response = Response(401, request=Request("GET", "https://api.todoist.com"))
            mock.get_projects.side_effect = HTTPStatusError(
                "Unauthorized", request=response.request, response=response
            )
            return mock

        monkeypatch.setattr("td.cli.config_cmd.TodoistAPI", bad_api)

        runner = CliRunner()
        result = runner.invoke(cli, ["init"], input="bad-token\n")

        assert result.exit_code == 1
        assert "copied the full token" in result.output

    def test_init_network_error_shows_specific_message(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        monkeypatch.setenv("TD_CONFIG_DIR", str(tmp_path))
        monkeypatch.delenv("TD_API_TOKEN", raising=False)

        from httpx import ConnectError

        def bad_api(token: str) -> MagicMock:
            mock = MagicMock()
            mock.get_projects.side_effect = ConnectError("Connection refused")
            return mock

        monkeypatch.setattr("td.cli.config_cmd.TodoistAPI", bad_api)

        runner = CliRunner()
        result = runner.invoke(cli, ["init"], input="bad-token\n")

        assert result.exit_code == 1
        assert "internet connection" in result.output

    def test_init_rate_limit_shows_specific_message(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        monkeypatch.setenv("TD_CONFIG_DIR", str(tmp_path))
        monkeypatch.delenv("TD_API_TOKEN", raising=False)

        from httpx import HTTPStatusError, Request, Response

        def bad_api(token: str) -> MagicMock:
            mock = MagicMock()
            response = Response(429, request=Request("GET", "https://api.todoist.com"))
            mock.get_projects.side_effect = HTTPStatusError(
                "Rate limited", request=response.request, response=response
            )
            return mock

        monkeypatch.setattr("td.cli.config_cmd.TodoistAPI", bad_api)

        runner = CliRunner()
        result = runner.invoke(cli, ["init"], input="bad-token\n")

        assert result.exit_code == 1
        assert "rate limit" in result.output


class TestCompletions:
    @pytest.mark.parametrize("shell", ["bash", "zsh", "fish"])
    def test_outputs_completion_script(self, shell: str) -> None:
        runner = CliRunner()
        result = runner.invoke(cli, ["completions", shell])

        assert result.exit_code == 0
        assert "_TD_COMPLETE" in result.output

    def test_rejects_invalid_shell(self) -> None:
        runner = CliRunner()
        result = runner.invoke(cli, ["completions", "powershell"])

        assert result.exit_code != 0
