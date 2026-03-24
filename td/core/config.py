"""Configuration loading, saving, and path resolution."""

from __future__ import annotations

import os
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

if sys.version_info >= (3, 11):
    import tomllib
else:
    try:
        import tomllib  # type: ignore[no-redef,import-not-found]
    except ModuleNotFoundError:
        import tomli as tomllib  # type: ignore[no-redef,import-not-found]

import tomli_w


def get_config_dir() -> Path:
    """Resolve config directory, respecting XDG_CONFIG_HOME and TD_CONFIG_DIR."""
    if env_dir := os.environ.get("TD_CONFIG_DIR"):
        return Path(env_dir)
    xdg = os.environ.get("XDG_CONFIG_HOME", "")
    base = Path(xdg) if xdg else Path.home() / ".config"
    return base / "td"


def get_config_path() -> Path:
    """Path to the config TOML file."""
    return get_config_dir() / "config.toml"


@dataclass
class TdConfig:
    """Application configuration."""

    api_token: str | None = None
    default_project: str | None = None
    default_format: str | None = None  # "rich", "plain", or "json"
    color: bool = True
    extra: dict[str, Any] = field(default_factory=dict)


def load_config() -> TdConfig:
    """Load config from TOML file, with env var overrides."""
    config = TdConfig()
    path = get_config_path()

    if path.exists():
        with open(path, "rb") as f:
            data = tomllib.load(f)

        auth = data.get("auth", {})
        config.api_token = auth.get("api_token")

        settings = data.get("settings", {})
        config.default_project = settings.get("default_project")
        config.default_format = settings.get("default_format")
        config.color = settings.get("color", True)

    # Env var overrides
    if token := os.environ.get("TD_API_TOKEN"):
        config.api_token = token

    if fmt := os.environ.get("TD_FORMAT"):
        config.default_format = fmt

    # Respect NO_COLOR (https://no-color.org/)
    if os.environ.get("NO_COLOR") is not None:
        config.color = False

    return config


def resolve_token() -> str | None:
    """Resolve API token from env or config file."""
    if token := os.environ.get("TD_API_TOKEN"):
        return token
    config = load_config()
    return config.api_token


def save_config(config: TdConfig) -> Path:
    """Save config to TOML file. Returns the path written to."""
    data: dict[str, Any] = {}

    if config.api_token:
        data["auth"] = {"api_token": config.api_token}

    settings: dict[str, Any] = {}
    if config.default_project:
        settings["default_project"] = config.default_project
    if not config.color:
        settings["color"] = False
    if settings:
        data["settings"] = settings

    path = get_config_path()
    path.parent.mkdir(parents=True, exist_ok=True)

    with open(path, "wb") as f:
        tomli_w.dump(data, f)

    return path
