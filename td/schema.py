"""Walk Click command tree to generate a JSON capability manifest."""

from __future__ import annotations

from typing import Any

import click

from td import __version__


def _click_type_to_str(param_type: click.ParamType) -> str:
    """Convert a Click parameter type to a human-readable string."""
    if isinstance(param_type, click.IntRange):
        return f"int({param_type.min}-{param_type.max})"
    if isinstance(param_type, click.Choice):
        return f"choice({','.join(param_type.choices)})"
    name = param_type.name
    return name if name else "string"


def _param_schema(param: click.Parameter) -> dict[str, Any]:
    """Extract schema for a single parameter."""
    schema: dict[str, Any] = {
        "name": param.name,
        "type": _click_type_to_str(param.type),
        "required": param.required,
    }
    if isinstance(param, click.Option):
        schema["flags"] = param.opts
        schema["help"] = param.help or ""
        schema["is_flag"] = param.is_flag
        if param.default is not None:
            try:
                # Only include JSON-serializable defaults
                import json

                json.dumps(param.default)
                schema["default"] = param.default
            except (TypeError, ValueError):
                pass
    return schema


def _command_schema(cmd: click.Command) -> dict[str, Any]:
    """Extract schema for a single command."""
    return {
        "description": cmd.help or "",
        "arguments": [
            _param_schema(p)
            for p in cmd.params
            if isinstance(p, click.Argument)
        ],
        "options": [
            _param_schema(p)
            for p in cmd.params
            if isinstance(p, click.Option)
            and p.name not in ("help",)
        ],
    }


def generate_schema(cli_group: click.Group) -> dict[str, Any]:
    """Walk the Click command tree and produce a capability manifest."""
    commands: dict[str, Any] = {}
    for name, cmd in sorted(cli_group.commands.items()):
        commands[name] = _command_schema(cmd)

    return {
        "name": "td",
        "version": __version__,
        "description": "AI-native Todoist CLI",
        "commands": commands,
    }
