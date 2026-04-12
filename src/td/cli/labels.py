"""Labels CLI commands.

Public surface: the ``label`` Click group (``add``, ``edit``, ``delete``,
``list``) plus the permanent flat plural alias ``labels``.

Hidden deprecated shims (``label-add``, ``label-edit``, ``label-delete``)
keep old invocations working through v0.13.0 with a stderr warning. They
will be removed in v0.14.0. See ADR-0009.
"""

from __future__ import annotations

from typing import Any, cast

import click

from td.cli.errors import TdValidationError
from td.cli.output import OutputFormatter
from td.core.client import get_client
from td.core.labels import _collect_labels, delete_label, resolve_label, update_label


def _get_formatter(ctx: click.Context) -> OutputFormatter:
    return cast(OutputFormatter, ctx.obj["formatter"])


def _list_labels(api: Any, fmt: OutputFormatter, search: str | None) -> None:
    """Shared listing implementation for ``td labels`` and ``td label list``."""
    if search:
        all_labels = [lbl for page in api.search_labels(query=search) for lbl in page]
    else:
        all_labels = _collect_labels(api)
    fmt.label_list(all_labels)


def _deprecation_notice(old: str, new: str) -> str:
    return f"Note: td {old} is now td {new}. The old name will be removed in v0.14.0."


# ---------------------------------------------------------------------------
# Permanent flat plural alias
# ---------------------------------------------------------------------------


@click.command()
@click.option("-s", "--search", help="Search labels by name.")
@click.pass_context
def labels(ctx: click.Context, search: str | None) -> None:
    """List all labels. Use -s to search by name."""
    _list_labels(get_client(), _get_formatter(ctx), search)


# ---------------------------------------------------------------------------
# label entity group (primary surface per ADR-0009)
# ---------------------------------------------------------------------------


@click.group(name="label", invoke_without_command=True)
@click.pass_context
def label(ctx: click.Context) -> None:
    """Manage Todoist labels (add, edit, delete, list)."""
    if ctx.invoked_subcommand is None:
        ctx.invoke(_label_list, search=None)


@label.command(name="list")
@click.option("-s", "--search", help="Search labels by name.")
@click.pass_context
def _label_list(ctx: click.Context, search: str | None) -> None:
    """List all labels. Use -s to search by name."""
    _list_labels(get_client(), _get_formatter(ctx), search)


@label.command(name="add")
@click.argument("name", nargs=-1, required=True)
@click.pass_context
def _label_add(ctx: click.Context, name: tuple[str, ...]) -> None:
    """Create a new label.

    \b
    Examples:
      td label add urgent
    """
    api = get_client()
    fmt = _get_formatter(ctx)

    lbl = api.add_label(name=" ".join(name))
    fmt.item_created("label", lbl)


@label.command(name="edit")
@click.argument("ref", nargs=-1, required=True)
@click.option("--name", help="New label name.")
@click.option("--color", help="New label color.")
@click.pass_context
def _label_edit(
    ctx: click.Context,
    ref: tuple[str, ...],
    name: str | None,
    color: str | None,
) -> None:
    """Rename or recolor a label. Ref is a name or ID.

    \b
    Examples:
      td label edit urgent --name critical
      td label edit low --color green
    """
    api = get_client()
    fmt = _get_formatter(ctx)

    if not name and not color:
        raise TdValidationError(
            "Nothing to update.",
            suggestion="Provide --name and/or --color.",
        )

    lbl = resolve_label(api, " ".join(ref))
    updated = update_label(api, lbl.id, name=name, color=color)
    fmt.success(
        f"Updated label: {updated.name}",
        {"label_id": updated.id, "name": updated.name},
    )


@label.command(name="delete")
@click.argument("ref", nargs=-1, required=True)
@click.option("-y", "--yes", is_flag=True, help="Skip confirmation.")
@click.pass_context
def _label_delete(ctx: click.Context, ref: tuple[str, ...], yes: bool) -> None:
    """Delete a label. Ref is a name or ID.

    \b
    Examples:
      td label delete old-label -y
    """
    api = get_client()
    fmt = _get_formatter(ctx)

    lbl = resolve_label(api, " ".join(ref))
    if not yes and not click.confirm(f'Delete label "{lbl.name}"?', default=False):
        click.echo("Aborted.")
        return

    delete_label(api, lbl.id)
    fmt.success(
        f"Deleted label: {lbl.name}",
        {"label_id": lbl.id, "name": lbl.name},
    )


# ---------------------------------------------------------------------------
# Hidden deprecated aliases (removed in v0.14.0)
# ---------------------------------------------------------------------------


@click.command(name="label-add", hidden=True)
@click.argument("name", nargs=-1, required=True)
@click.pass_context
def label_add(ctx: click.Context, name: tuple[str, ...]) -> None:
    """Deprecated: use ``td label add``."""
    click.echo(_deprecation_notice("label-add", "label add"), err=True)
    ctx.invoke(_label_add, name=name)


@click.command(name="label-edit", hidden=True)
@click.argument("ref", nargs=-1, required=True)
@click.option("--name")
@click.option("--color")
@click.pass_context
def label_edit(
    ctx: click.Context,
    ref: tuple[str, ...],
    name: str | None,
    color: str | None,
) -> None:
    """Deprecated: use ``td label edit``."""
    click.echo(_deprecation_notice("label-edit", "label edit"), err=True)
    ctx.invoke(_label_edit, ref=ref, name=name, color=color)


@click.command(name="label-delete", hidden=True)
@click.argument("ref", nargs=-1, required=True)
@click.option("-y", "--yes", is_flag=True)
@click.pass_context
def label_delete(ctx: click.Context, ref: tuple[str, ...], yes: bool) -> None:
    """Deprecated: use ``td label delete``."""
    click.echo(_deprecation_notice("label-delete", "label delete"), err=True)
    ctx.invoke(_label_delete, ref=ref, yes=yes)
