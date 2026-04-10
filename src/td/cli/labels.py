"""Labels CLI commands."""

from __future__ import annotations

import sys
from typing import cast

import click

from td.cli.errors import TdValidationError
from td.cli.output import OutputFormatter
from td.core.client import get_client
from td.core.labels import _collect_labels, delete_label, resolve_label, update_label


def _get_formatter(ctx: click.Context) -> OutputFormatter:
    return cast(OutputFormatter, ctx.obj["formatter"])


@click.command()
@click.option("-s", "--search", help="Search labels by name.")
@click.pass_context
def labels(ctx: click.Context, search: str | None) -> None:
    """List all labels. Use -s to search by name."""
    api = get_client()
    fmt = _get_formatter(ctx)

    if search:
        all_labels = [lbl for page in api.search_labels(query=search) for lbl in page]
    else:
        all_labels = _collect_labels(api)

    fmt.label_list(all_labels)


@click.command(name="label-add")
@click.argument("name", nargs=-1, required=True)
@click.pass_context
def label_add(ctx: click.Context, name: tuple[str, ...]) -> None:
    """Create a new label."""
    api = get_client()
    fmt = _get_formatter(ctx)

    label = api.add_label(name=" ".join(name))
    fmt.item_created("label", label)


@click.command(name="label-edit")
@click.argument("ref", nargs=-1, required=True)
@click.option("--name", help="New label name.")
@click.option("--color", help="New label color.")
@click.pass_context
def label_edit(
    ctx: click.Context,
    ref: tuple[str, ...],
    name: str | None,
    color: str | None,
) -> None:
    """Rename or recolor a label. Ref is a name or ID.

    \b
    Examples:
      td label-edit urgent --name critical
      td label-edit low --color green
    """
    api = get_client()
    fmt = _get_formatter(ctx)

    if not name and not color:
        raise TdValidationError(
            "Nothing to update.",
            suggestion="Provide --name and/or --color.",
        )

    label = resolve_label(api, " ".join(ref))
    updated = update_label(api, label.id, name=name, color=color)
    fmt.success(
        f"Updated label: {updated.name}",
        {"label_id": updated.id, "name": updated.name},
    )


@click.command(name="label-delete")
@click.argument("ref", nargs=-1, required=True)
@click.option("-y", "--yes", is_flag=True, help="Skip confirmation.")
@click.pass_context
def label_delete(ctx: click.Context, ref: tuple[str, ...], yes: bool) -> None:
    """Delete a label. Ref is a name or ID.

    \b
    Examples:
      td label-delete old-label -y
    """
    api = get_client()
    fmt = _get_formatter(ctx)

    label = resolve_label(api, " ".join(ref))
    if not yes:
        if not sys.stdout.isatty():
            raise TdValidationError(
                "Cannot confirm deletion in non-interactive mode.",
                suggestion="Use --yes flag to skip confirmation.",
            )
        if not click.confirm(f'Delete label "{label.name}"?'):
            click.echo("Aborted.")
            return

    delete_label(api, label.id)
    fmt.success(
        f"Deleted label: {label.name}",
        {"label_id": label.id, "name": label.name},
    )
