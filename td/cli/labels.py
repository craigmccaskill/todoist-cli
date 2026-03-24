"""Labels CLI command."""

from __future__ import annotations

import click

from td.cli.output import OutputFormatter
from td.core.client import get_client
from td.core.labels import _collect_labels


def _get_formatter(ctx: click.Context) -> OutputFormatter:
    return ctx.obj["formatter"]  # type: ignore[no-any-return]


@click.command()
@click.option("-s", "--search", help="Search labels by name.")
@click.pass_context
def labels(ctx: click.Context, search: str | None) -> None:
    """List all labels."""
    api = get_client()
    fmt = _get_formatter(ctx)

    if search:
        all_labels = [
            lbl
            for page in api.search_labels(query=search)
            for lbl in page
        ]
    else:
        all_labels = _collect_labels(api)

    fmt.label_list(all_labels)
