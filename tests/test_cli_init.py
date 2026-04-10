"""Tests for td init and td completions commands."""

from __future__ import annotations

import os
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
        # Prevent completions prompt from interfering
        monkeypatch.setattr("td.cli.config_cmd._detect_shell", lambda: None)

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
        monkeypatch.setattr("td.cli.config_cmd._detect_shell", lambda: None)

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
        monkeypatch.setattr("td.cli.config_cmd._detect_shell", lambda: None)

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
        monkeypatch.setattr("td.cli.config_cmd._detect_shell", lambda: None)

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

    def test_init_offers_completions(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        monkeypatch.setenv("TD_CONFIG_DIR", str(tmp_path))
        monkeypatch.delenv("TD_API_TOKEN", raising=False)

        mock_api = MagicMock()
        mock_api.get_projects.return_value = iter([[MagicMock()]])
        monkeypatch.setattr("td.cli.config_cmd.TodoistAPI", lambda token: mock_api)
        monkeypatch.setattr("td.cli.config_cmd._detect_shell", lambda: "zsh")
        monkeypatch.setattr(
            "td.cli.config_cmd._is_completion_installed",
            lambda shell: (False, tmp_path / ".zshrc"),
        )

        installed_calls: list[str] = []

        def mock_install(shell: str) -> tuple[bool, Path]:
            installed_calls.append(shell)
            return True, tmp_path / ".zshrc"

        monkeypatch.setattr("td.cli.config_cmd._install_completions", mock_install)
        monkeypatch.setattr("td.cli.config_cmd._check_path_collision", lambda: None)

        runner = CliRunner()
        # token + choice 1 + Y for completions
        result = runner.invoke(cli, ["init"], input="test-token\n1\nY\n")

        assert result.exit_code == 0
        assert len(installed_calls) == 1
        assert installed_calls[0] == "zsh"
        assert "Completions added" in result.output

    def test_init_skips_completions_when_declined(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        monkeypatch.setenv("TD_CONFIG_DIR", str(tmp_path))
        monkeypatch.delenv("TD_API_TOKEN", raising=False)

        mock_api = MagicMock()
        mock_api.get_projects.return_value = iter([[MagicMock()]])
        monkeypatch.setattr("td.cli.config_cmd.TodoistAPI", lambda token: mock_api)
        monkeypatch.setattr("td.cli.config_cmd._detect_shell", lambda: "zsh")
        monkeypatch.setattr(
            "td.cli.config_cmd._is_completion_installed",
            lambda shell: (False, tmp_path / ".zshrc"),
        )
        monkeypatch.setattr("td.cli.config_cmd._check_path_collision", lambda: None)

        runner = CliRunner()
        result = runner.invoke(cli, ["init"], input="test-token\n1\nn\n")

        assert result.exit_code == 0
        assert "Completions added" not in result.output

    def test_init_skips_completions_when_already_installed(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        monkeypatch.setenv("TD_CONFIG_DIR", str(tmp_path))
        monkeypatch.delenv("TD_API_TOKEN", raising=False)

        mock_api = MagicMock()
        mock_api.get_projects.return_value = iter([[MagicMock()]])
        monkeypatch.setattr("td.cli.config_cmd.TodoistAPI", lambda token: mock_api)
        monkeypatch.setattr("td.cli.config_cmd._detect_shell", lambda: "zsh")
        monkeypatch.setattr(
            "td.cli.config_cmd._is_completion_installed",
            lambda shell: (True, tmp_path / ".zshrc"),
        )
        monkeypatch.setattr("td.cli.config_cmd._check_path_collision", lambda: None)

        runner = CliRunner()
        result = runner.invoke(cli, ["init"], input="test-token\n1\n")

        assert result.exit_code == 0
        # Should not prompt about completions since already installed
        assert "Enable shell completions" not in result.output


class TestCompletionsStatus:
    def test_status_not_installed(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        monkeypatch.setenv("SHELL", "/bin/zsh")
        monkeypatch.setattr("td.cli.config_cmd._get_profile_path", lambda s: tmp_path / ".zshrc")

        runner = CliRunner()
        result = runner.invoke(cli, ["completions"])

        assert result.exit_code == 0
        assert "zsh" in result.output
        assert "not installed" in result.output
        assert "td completions install" in result.output

    def test_status_installed(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        monkeypatch.setenv("SHELL", "/bin/zsh")
        profile = tmp_path / ".zshrc"
        profile.write_text('eval "$(_TD_COMPLETE=zsh_source td)"\n')
        monkeypatch.setattr("td.cli.config_cmd._get_profile_path", lambda s: profile)

        runner = CliRunner()
        result = runner.invoke(cli, ["completions"])

        assert result.exit_code == 0
        assert "zsh" in result.output
        assert "installed" in result.output
        assert "not installed" not in result.output

    def test_status_with_shell_override(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        monkeypatch.setattr("td.cli.config_cmd._get_profile_path", lambda s: tmp_path / ".bashrc")

        runner = CliRunner()
        result = runner.invoke(cli, ["completions", "--shell", "bash"])

        assert result.exit_code == 0
        assert "bash" in result.output
        assert "not installed" in result.output

    def test_status_unsupported_shell(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("SHELL", "/bin/csh")

        runner = CliRunner()
        result = runner.invoke(cli, ["completions"])

        assert result.exit_code != 0
        assert "Could not detect shell" in result.output


class TestCompletionsInstall:
    def test_install_creates_line(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        monkeypatch.setenv("SHELL", "/bin/zsh")
        profile = tmp_path / ".zshrc"
        profile.write_text("# existing config\n")
        monkeypatch.setattr("td.cli.config_cmd._get_profile_path", lambda s: profile)

        runner = CliRunner()
        result = runner.invoke(cli, ["completions", "install"])

        assert result.exit_code == 0
        assert "installed" in result.output.lower()
        content = profile.read_text()
        assert 'eval "$(_TD_COMPLETE=zsh_source td)"' in content

    def test_install_idempotent(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        monkeypatch.setenv("SHELL", "/bin/zsh")
        profile = tmp_path / ".zshrc"
        profile.write_text('eval "$(_TD_COMPLETE=zsh_source td)"\n')
        monkeypatch.setattr("td.cli.config_cmd._get_profile_path", lambda s: profile)

        runner = CliRunner()
        result = runner.invoke(cli, ["completions", "install"])

        assert result.exit_code == 0
        assert "already installed" in result.output.lower()
        # Verify line not duplicated
        content = profile.read_text()
        assert content.count("_TD_COMPLETE") == 1

    def test_install_bash(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        monkeypatch.setenv("SHELL", "/bin/bash")
        profile = tmp_path / ".bashrc"
        profile.write_text("")
        monkeypatch.setattr("td.cli.config_cmd._get_profile_path", lambda s: profile)

        runner = CliRunner()
        result = runner.invoke(cli, ["completions", "install"])

        assert result.exit_code == 0
        content = profile.read_text()
        assert 'eval "$(_TD_COMPLETE=bash_source td)"' in content

    def test_install_fish(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        monkeypatch.setenv("SHELL", "/usr/bin/fish")
        fish_dir = tmp_path / ".config" / "fish"
        fish_dir.mkdir(parents=True)
        profile = fish_dir / "config.fish"
        profile.write_text("")
        monkeypatch.setattr("td.cli.config_cmd._get_profile_path", lambda s: profile)

        runner = CliRunner()
        result = runner.invoke(cli, ["completions", "install"])

        assert result.exit_code == 0
        content = profile.read_text()
        assert "_TD_COMPLETE=fish_source td | source" in content

    def test_install_creates_profile_if_missing(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        monkeypatch.setenv("SHELL", "/bin/zsh")
        profile = tmp_path / ".zshrc"
        # Don't create the file
        monkeypatch.setattr("td.cli.config_cmd._get_profile_path", lambda s: profile)

        runner = CliRunner()
        result = runner.invoke(cli, ["completions", "install"])

        assert result.exit_code == 0
        assert profile.exists()
        assert "_TD_COMPLETE" in profile.read_text()

    def test_install_unsupported_shell(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("SHELL", "/bin/csh")

        runner = CliRunner()
        result = runner.invoke(cli, ["completions", "install"])

        assert result.exit_code != 0
        assert "Could not detect shell" in result.output


class TestCompletionsUninstall:
    def test_uninstall_removes_line(self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
        monkeypatch.setenv("SHELL", "/bin/zsh")
        profile = tmp_path / ".zshrc"
        profile.write_text('# my config\neval "$(_TD_COMPLETE=zsh_source td)"\n# other stuff\n')
        monkeypatch.setattr("td.cli.config_cmd._get_profile_path", lambda s: profile)

        runner = CliRunner()
        result = runner.invoke(cli, ["completions", "uninstall"])

        assert result.exit_code == 0
        assert "removed" in result.output.lower()
        content = profile.read_text()
        assert "_TD_COMPLETE" not in content
        assert "my config" in content
        assert "other stuff" in content

    def test_uninstall_noop_when_not_installed(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        monkeypatch.setenv("SHELL", "/bin/zsh")
        profile = tmp_path / ".zshrc"
        profile.write_text("# just comments\n")
        monkeypatch.setattr("td.cli.config_cmd._get_profile_path", lambda s: profile)

        runner = CliRunner()
        result = runner.invoke(cli, ["completions", "uninstall"])

        assert result.exit_code == 0
        assert "no completions found" in result.output.lower()

    def test_uninstall_noop_when_no_profile(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        monkeypatch.setenv("SHELL", "/bin/zsh")
        profile = tmp_path / ".zshrc"
        monkeypatch.setattr("td.cli.config_cmd._get_profile_path", lambda s: profile)

        runner = CliRunner()
        result = runner.invoke(cli, ["completions", "uninstall"])

        assert result.exit_code == 0
        assert "no completions found" in result.output.lower()


class TestCompletionsShow:
    def test_show_zsh(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("SHELL", "/bin/zsh")

        runner = CliRunner()
        result = runner.invoke(cli, ["completions", "show"])

        assert result.exit_code == 0
        assert "zsh_source" in result.output
        assert "_TD_COMPLETE" in result.output

    def test_show_bash(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("SHELL", "/bin/bash")

        runner = CliRunner()
        result = runner.invoke(cli, ["completions", "show"])

        assert result.exit_code == 0
        assert "bash_source" in result.output

    def test_show_fish(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("SHELL", "/usr/bin/fish")

        runner = CliRunner()
        result = runner.invoke(cli, ["completions", "show"])

        assert result.exit_code == 0
        assert "fish_source" in result.output

    def test_show_with_shell_override(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setenv("SHELL", "/bin/zsh")

        runner = CliRunner()
        result = runner.invoke(cli, ["completions", "--shell", "bash", "show"])

        assert result.exit_code == 0
        assert "bash_source" in result.output


class TestPathCollision:
    def test_no_collision(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """When there is only one td on PATH, no warning."""
        from td.cli.config_cmd import _check_path_collision

        monkeypatch.setattr("td.cli.config_cmd.shutil.which", lambda name: "/usr/local/bin/td")
        monkeypatch.setenv("PATH", "/usr/local/bin")

        # Mock Path.exists and is_file for the single candidate
        original_exists = Path.exists
        original_is_file = Path.is_file

        def mock_exists(self: Path) -> bool:
            if str(self) == "/usr/local/bin/td":
                return True
            return original_exists(self)

        def mock_is_file(self: Path) -> bool:
            if str(self) == "/usr/local/bin/td":
                return True
            return original_is_file(self)

        monkeypatch.setattr(Path, "exists", mock_exists)
        monkeypatch.setattr(Path, "is_file", mock_is_file)

        result = _check_path_collision()
        assert result is None

    def test_collision_detected(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """When multiple td binaries exist, a warning is returned."""
        from td.cli.config_cmd import _check_path_collision

        monkeypatch.setattr("td.cli.config_cmd.shutil.which", lambda name: "/usr/local/bin/td")
        monkeypatch.setenv("PATH", "/usr/local/bin:/home/user/.local/bin")

        # Both directories have a td binary
        original_exists = Path.exists
        original_is_file = Path.is_file

        td_paths = {"/usr/local/bin/td", "/home/user/.local/bin/td"}

        def mock_exists(self: Path) -> bool:
            if str(self) in td_paths:
                return True
            return original_exists(self)

        def mock_is_file(self: Path) -> bool:
            if str(self) in td_paths:
                return True
            return original_is_file(self)

        def mock_resolve(self: Path) -> Path:
            # Return the path as-is for our test paths
            if str(self) in td_paths:
                return self
            return Path(os.path.realpath(str(self)))

        monkeypatch.setattr(Path, "exists", mock_exists)
        monkeypatch.setattr(Path, "is_file", mock_is_file)
        monkeypatch.setattr(Path, "resolve", mock_resolve)

        # sys.executable is in /home/user/.local/bin
        monkeypatch.setattr("td.cli.config_cmd.sys.executable", "/home/user/.local/bin/python")

        result = _check_path_collision()
        assert result is not None
        assert "already on your PATH" in result
        assert "alias" in result

    def test_collision_nonblocking_in_init(
        self, monkeypatch: pytest.MonkeyPatch, tmp_path: Path
    ) -> None:
        """PATH collision warning does not prevent init from completing."""
        monkeypatch.setenv("TD_CONFIG_DIR", str(tmp_path))
        monkeypatch.delenv("TD_API_TOKEN", raising=False)

        mock_api = MagicMock()
        mock_api.get_projects.return_value = iter([[MagicMock()]])
        monkeypatch.setattr("td.cli.config_cmd.TodoistAPI", lambda token: mock_api)
        monkeypatch.setattr("td.cli.config_cmd._detect_shell", lambda: None)
        monkeypatch.setattr(
            "td.cli.config_cmd._check_path_collision",
            lambda: '"td" is already on your PATH (/usr/local/bin/td)',
        )

        runner = CliRunner()
        result = runner.invoke(cli, ["init"], input="test-token\n1\n")

        assert result.exit_code == 0
        assert "already on your PATH" in result.output
        assert "Try `td ls`" in result.output  # init completed successfully

    def test_no_td_on_path(self, monkeypatch: pytest.MonkeyPatch) -> None:
        """When td is not found on PATH at all."""
        from td.cli.config_cmd import _check_path_collision

        monkeypatch.setattr("td.cli.config_cmd.shutil.which", lambda name: None)

        result = _check_path_collision()
        assert result is None
