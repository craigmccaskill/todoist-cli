"""Environment diagnostics — pure business logic, no CLI dependency."""

from __future__ import annotations

import os
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from td import __version__
from td.core.config import get_config_path, load_config


@dataclass
class CheckResult:
    """Single diagnostic check result."""

    name: str
    status: str  # "pass", "fail", "warn"
    detail: str
    suggestion: str = ""

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dict for JSON output."""
        d: dict[str, Any] = {
            "name": self.name,
            "status": self.status,
            "detail": self.detail,
        }
        if self.suggestion:
            d["suggestion"] = self.suggestion
        return d


def check_version() -> CheckResult:
    """Report td version."""
    return CheckResult(
        name="td version",
        status="pass",
        detail=f"v{__version__}",
    )


def check_python_version() -> CheckResult:
    """Report Python version (always pass)."""
    version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    return CheckResult(
        name="Python version",
        status="pass",
        detail=version,
    )


def check_config_file() -> CheckResult:
    """Check if config file exists and is valid TOML."""
    path = get_config_path()
    if not path.exists():
        return CheckResult(
            name="Config file",
            status="warn",
            detail=f"Not found at {path}",
            suggestion="Run `td init` to create a config file.",
        )

    try:
        try:
            import tomllib  # type: ignore[import-not-found]
        except ModuleNotFoundError:
            import tomli as tomllib  # type: ignore[import-not-found,no-redef]

        with open(path, "rb") as f:
            tomllib.load(f)
        return CheckResult(
            name="Config file",
            status="pass",
            detail=str(path),
        )
    except Exception as e:
        return CheckResult(
            name="Config file",
            status="fail",
            detail=f"Invalid TOML at {path}: {e}",
            suggestion="Fix the syntax or delete the file and run `td init`.",
        )


def check_api_token() -> CheckResult:
    """Check if an API token is available and report its source."""
    env_token = os.environ.get("TD_API_TOKEN")
    config = load_config()

    if env_token:
        return CheckResult(
            name="API token",
            status="pass",
            detail="Set via TD_API_TOKEN environment variable",
        )

    if config.api_token:
        return CheckResult(
            name="API token",
            status="pass",
            detail="Set via config file",
        )

    return CheckResult(
        name="API token",
        status="fail",
        detail="No API token found",
        suggestion="Run `td init` or set TD_API_TOKEN.",
    )


def check_api_connectivity() -> CheckResult:
    """Ping the Todoist API with a lightweight call."""
    from td.core.config import resolve_token

    token = resolve_token()
    if not token:
        return CheckResult(
            name="API connectivity",
            status="fail",
            detail="Skipped (no API token)",
            suggestion="Set an API token first, then re-run `td doctor`.",
        )

    try:
        from todoist_api_python.api import TodoistAPI

        api = TodoistAPI(token)
        projects = api.get_projects()
        count = len(list(projects))
        return CheckResult(
            name="API connectivity",
            status="pass",
            detail=f"OK ({count} project(s))",
        )
    except Exception as e:
        return CheckResult(
            name="API connectivity",
            status="fail",
            detail=f"Failed: {e}",
            suggestion="Check your internet connection and API token.",
        )


def check_shell_completions() -> CheckResult:
    """Check if shell completions are configured."""
    shell_path = os.environ.get("SHELL", "")
    shell_name = ""
    for name in ("bash", "zsh", "fish"):
        if name in shell_path:
            shell_name = name
            break

    if not shell_name:
        return CheckResult(
            name="Shell completions",
            status="warn",
            detail=f"Unknown shell: {shell_path or '(not set)'}",
            suggestion="Run `td completions [bash|zsh|fish]` for setup instructions.",
        )

    profile_map = {
        "bash": [Path.home() / ".bashrc", Path.home() / ".bash_profile"],
        "zsh": [Path.home() / ".zshrc"],
        "fish": [Path.home() / ".config" / "fish" / "config.fish"],
    }

    profiles = profile_map.get(shell_name, [])
    completion_marker = "_TD_COMPLETE"

    for profile in profiles:
        if profile.exists():
            try:
                content = profile.read_text()
                if completion_marker in content:
                    return CheckResult(
                        name="Shell completions",
                        status="pass",
                        detail=f"Configured in {profile}",
                    )
            except OSError:
                continue

    return CheckResult(
        name="Shell completions",
        status="warn",
        detail=f"Not found in {shell_name} profile",
        suggestion=f"Run `td completions {shell_name}` and add the output to your shell profile.",
    )


def check_path_conflicts() -> CheckResult:
    """Check if another `td` binary exists on PATH."""
    td_paths: list[str] = []
    seen: set[str] = set()

    for directory in os.environ.get("PATH", "").split(os.pathsep):
        if not directory:
            continue
        candidate = shutil.which("td", path=directory)
        if candidate and candidate not in seen:
            seen.add(candidate)
            td_paths.append(candidate)

    if len(td_paths) <= 1:
        location = td_paths[0] if td_paths else "not found on PATH"
        return CheckResult(
            name="PATH conflicts",
            status="pass",
            detail=location,
        )

    return CheckResult(
        name="PATH conflicts",
        status="warn",
        detail=f"Multiple `td` found: {', '.join(td_paths)}",
        suggestion="Ensure the correct `td` appears first in your PATH.",
    )


def run_all_checks(*, skip_api: bool = False) -> list[CheckResult]:
    """Run all diagnostic checks and return results.

    Args:
        skip_api: If True, skip the API connectivity check (useful for testing).
    """
    results = [
        check_version(),
        check_python_version(),
        check_config_file(),
        check_api_token(),
    ]

    if not skip_api:
        results.append(check_api_connectivity())

    results.extend(
        [
            check_shell_completions(),
            check_path_conflicts(),
        ]
    )

    return results
