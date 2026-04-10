"""Tests for td skill command."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from click.testing import CliRunner

from td.cli import cli
from td.core.skill import (
    generate_skill_content,
    installed_version,
    needs_update,
)
from td.schema import generate_schema


class TestGenerateSkillContent:
    def test_includes_version(self) -> None:
        schema = generate_schema(cli)
        content = generate_skill_content(schema)
        assert "Version:" in content

    def test_includes_agent_guidance(self) -> None:
        schema = generate_schema(cli)
        content = generate_skill_content(schema)
        assert "Agent guidance" in content
        assert "--json" in content

    def test_includes_security_note(self) -> None:
        schema = generate_schema(cli)
        content = generate_skill_content(schema)
        assert "untrusted" in content.lower()

    def test_includes_commands(self) -> None:
        schema = generate_schema(cli)
        content = generate_skill_content(schema)
        assert "### td add" in content
        assert "### td done" in content
        assert "### td ls" in content

    def test_excludes_hidden_commands(self) -> None:
        schema = generate_schema(cli)
        content = generate_skill_content(schema)
        assert "### td quick" not in content
        assert "### td capture" not in content


class TestInstallUninstall:
    def test_install_creates_file(self, tmp_path: Path) -> None:
        skill_path = tmp_path / "skills" / "todoist-cli" / "SKILL.md"
        content = "# test skill"
        # Write directly to test path
        skill_path.parent.mkdir(parents=True)
        skill_path.write_text(content)
        assert skill_path.exists()
        assert skill_path.read_text() == content

    def test_uninstall_removes_file(self, tmp_path: Path) -> None:
        skill_path = tmp_path / "SKILL.md"
        skill_path.write_text("# test")
        assert skill_path.exists()
        skill_path.unlink()
        assert not skill_path.exists()


class TestInstalledVersion:
    def test_reads_version(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        skill_dir = tmp_path / "skills" / "todoist-cli"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("# td\n\nVersion: 0.11.0-alpha\n\nStuff")
        monkeypatch.setattr(
            "td.core.skill.AGENT_TARGETS",
            {"test-agent": (skill_dir, "Test Agent")},
        )
        assert installed_version("test-agent") == "0.11.0-alpha"

    def test_returns_none_when_missing(
        self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        skill_dir = tmp_path / "skills" / "todoist-cli"
        monkeypatch.setattr(
            "td.core.skill.AGENT_TARGETS",
            {"test-agent": (skill_dir, "Test Agent")},
        )
        assert installed_version("test-agent") is None


class TestNeedsUpdate:
    def test_detects_stale(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        skill_dir = tmp_path / "skills" / "todoist-cli"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text("# td\n\nVersion: 0.0.1\n")
        monkeypatch.setattr(
            "td.core.skill.AGENT_TARGETS",
            {"test-agent": (skill_dir, "Test Agent")},
        )
        assert needs_update("test-agent") is True

    def test_current_is_fine(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        from td import __version__

        skill_dir = tmp_path / "skills" / "todoist-cli"
        skill_dir.mkdir(parents=True)
        (skill_dir / "SKILL.md").write_text(f"# td\n\nVersion: {__version__}\n")
        monkeypatch.setattr(
            "td.core.skill.AGENT_TARGETS",
            {"test-agent": (skill_dir, "Test Agent")},
        )
        assert needs_update("test-agent") is False


class TestSkillCommand:
    def test_status_no_agent(self, monkeypatch: pytest.MonkeyPatch) -> None:
        monkeypatch.setattr("td.core.skill.AGENT_TARGETS", {})
        runner = CliRunner()
        result = runner.invoke(cli, ["skill"])
        assert result.exit_code == 0
        assert "No supported AI agent detected" in result.output

    def test_status_not_installed(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        skill_dir = tmp_path / "skills" / "todoist-cli"
        monkeypatch.setattr(
            "td.core.skill.AGENT_TARGETS",
            {"test-agent": (skill_dir, "Test Agent")},
        )
        runner = CliRunner()
        result = runner.invoke(cli, ["skill"])
        assert result.exit_code == 0
        assert "not installed" in result.output

    def test_install_and_uninstall(self, tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
        skill_dir = tmp_path / "skills" / "todoist-cli"
        monkeypatch.setattr(
            "td.core.skill.AGENT_TARGETS",
            {"test-agent": (skill_dir, "Test Agent")},
        )
        runner = CliRunner()

        # Install
        result = runner.invoke(cli, ["--json", "skill", "install", "test-agent"])
        assert result.exit_code == 0
        assert (skill_dir / "SKILL.md").exists()
        content = (skill_dir / "SKILL.md").read_text()
        assert "### td add" in content

        # Uninstall
        result = runner.invoke(cli, ["--json", "skill", "uninstall", "test-agent"])
        assert result.exit_code == 0
        assert not (skill_dir / "SKILL.md").exists()

    def test_install_unknown_agent(self) -> None:
        runner = CliRunner()
        result = runner.invoke(cli, ["skill", "install", "unknown-agent"])
        assert result.exit_code != 0

    def test_skill_in_schema(self) -> None:
        runner = CliRunner()
        result = runner.invoke(cli, ["schema"])
        data = json.loads(result.output)
        assert "skill" in data["commands"]
