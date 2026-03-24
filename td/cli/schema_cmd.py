"""Schema command — output capability manifest as JSON."""

from __future__ import annotations

import json

import click


@click.command()
def schema() -> None:
    """Output full capability manifest as JSON."""
    from td.cli import cli
    from td.schema import generate_schema

    manifest = generate_schema(cli)
    click.echo(json.dumps(manifest, indent=2))
