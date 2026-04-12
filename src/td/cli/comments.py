"""Comments CLI commands.

The ``comment`` command is a Click group with a custom
:class:`CommentGroup` subclass that delegates to the ``add`` subcommand
when the first positional argument is not one of the group's known
subcommand names. This preserves the permanent flat shortcut
``td comment <task_ref> <text>`` without requiring an explicit ``add``
verb, while still exposing ``add``, ``edit``, ``delete``, and ``list``
as discoverable subcommands under ``td comment --help``.

The plural ``comments`` command is a separate flat list alias (same
pattern as ``projects``, ``sections``, ``labels``).

Hidden deprecated shims ``comment-edit`` and ``comment-delete`` keep old
invocations working through v0.13.0 with a stderr warning. They will be
removed in v0.14.0. See ADR-0009 for the full grammar decision.
"""

from __future__ import annotations

from typing import Any, cast

import click

from td.cli.errors import TdValidationError
from td.cli.output import OutputFormatter
from td.core.client import get_client


def _get_formatter(ctx: click.Context) -> OutputFormatter:
    return cast(OutputFormatter, ctx.obj["formatter"])


def _require_task(ref: str | None, api: Any) -> str:
    """Resolve task ref, launching picker if empty and TTY."""
    from td.cli.tasks import _require_task_ref

    return _require_task_ref((ref,) if ref else (), api)


def _deprecation_notice(old: str, new: str) -> str:
    return f"Note: td {old} is now td {new}. The old name will be removed in v0.14.0."


class CommentGroup(click.Group):
    """Click group that falls through to ``add`` when the first positional
    argument isn't a known subcommand.

    Preserves the permanent flat shortcut ``td comment 1 "text"``
    alongside the discoverable ``td comment add``, ``td comment edit``,
    ``td comment delete``, ``td comment list`` subcommands. The only
    ambiguity is a task literally named after a subcommand verb (e.g.
    a task called "edit"); that case routes to the subcommand and the
    user can disambiguate with ``td comment add edit "text"``.
    """

    def resolve_command(
        self,
        ctx: click.Context,
        args: list[str],
    ) -> tuple[str | None, click.Command | None, list[str]]:
        if args and args[0] in self.commands:
            return super().resolve_command(ctx, args)
        add_cmd = self.commands.get("add")
        if add_cmd is None:
            return super().resolve_command(ctx, args)
        return "add", add_cmd, args


# ---------------------------------------------------------------------------
# Permanent flat plural alias for the list case.
# ---------------------------------------------------------------------------


@click.command()
@click.argument("task_ref", required=False, default=None)
@click.pass_context
def comments(ctx: click.Context, task_ref: str | None) -> None:
    """List comments on a task. Accepts row number, content match, or task ID.

    \b
    Examples:
      td comments 1
      td comments buy milk
    """
    api = get_client()
    fmt = _get_formatter(ctx)
    task_id = _require_task(task_ref, api)

    all_comments = [c for page in api.get_comments(task_id=task_id) for c in page]
    fmt.comment_list(all_comments)


# ---------------------------------------------------------------------------
# comment entity group (primary surface per ADR-0009)
#
# Uses CommentGroup to preserve the permanent flat shortcut
# ``td comment <task_ref> <text>`` when the first positional isn't a
# known subcommand name.
# ---------------------------------------------------------------------------


@click.group(name="comment", cls=CommentGroup)
@click.pass_context
def comment(ctx: click.Context) -> None:
    """Manage task comments (add, edit, delete, list).

    Permanent flat shortcut preserved:

    \b
      td comment 1 "Picked up 2%, not whole"
      td comment buy milk "Got oat milk instead"

    Explicit subcommands also available:

    \b
      td comment add 1 "Picked up 2%"
      td comment edit <comment_id> --content "Updated text"
      td comment delete <comment_id> -y
      td comment list 1
    """
    # All behavior is in subcommands; CommentGroup.resolve_command handles
    # the fall-through case to ``add`` for the flat shortcut.


@comment.command(name="add")
@click.argument("task_ref", required=False, default=None)
@click.argument("text", nargs=-1, required=True)
@click.pass_context
def _comment_add(
    ctx: click.Context,
    task_ref: str | None,
    text: tuple[str, ...],
) -> None:
    """Add a comment to a task. Accepts row number, content match, or task ID.

    \b
    Examples:
      td comment add 1 "Picked up 2%, not whole"
      td comment buy milk "Got oat milk instead"    # flat shortcut also works
    """
    api = get_client()
    fmt = _get_formatter(ctx)
    task_id = _require_task(task_ref, api)

    result = api.add_comment(content=" ".join(text), task_id=task_id)
    fmt.success(
        f"Comment added to task {task_id}",
        {"comment_id": result.id, "task_id": task_id, "content": result.content},
    )


@comment.command(name="list")
@click.argument("task_ref", required=False, default=None)
@click.pass_context
def _comment_list(ctx: click.Context, task_ref: str | None) -> None:
    """List comments on a task. Same as ``td comments``."""
    api = get_client()
    fmt = _get_formatter(ctx)
    task_id = _require_task(task_ref, api)

    all_comments = [c for page in api.get_comments(task_id=task_id) for c in page]
    fmt.comment_list(all_comments)


@comment.command(name="edit")
@click.argument("comment_id")
@click.argument("content", nargs=-1)
@click.option("--content", "content_flag", help="New comment content.")
@click.pass_context
def _comment_edit(
    ctx: click.Context,
    comment_id: str,
    content: tuple[str, ...],
    content_flag: str | None,
) -> None:
    """Update a comment's content. Content as positional args or --content flag.

    \b
    Examples:
      td comment edit abc123 "Updated text"
      td comment edit abc123 --content "Updated text"
    """
    api = get_client()
    fmt = _get_formatter(ctx)

    new_content = content_flag or (" ".join(content) if content else "")
    if not new_content:
        raise TdValidationError(
            "No content provided.",
            suggestion="Provide new content as an argument or with --content.",
        )

    result = api.update_comment(comment_id, content=new_content)
    fmt.success(
        f"Updated comment {comment_id}",
        {"comment_id": result.id, "content": result.content},
    )


@comment.command(name="delete")
@click.argument("comment_id")
@click.option("-y", "--yes", is_flag=True, help="Skip confirmation.")
@click.pass_context
def _comment_delete(ctx: click.Context, comment_id: str, yes: bool) -> None:
    """Delete a comment by ID.

    \b
    Examples:
      td comment delete abc123 -y
    """
    api = get_client()
    fmt = _get_formatter(ctx)

    if not yes and not click.confirm(f"Delete comment {comment_id}?", default=False):
        click.echo("Aborted.")
        return

    api.delete_comment(comment_id)
    fmt.success(
        f"Deleted comment {comment_id}",
        {"comment_id": comment_id},
    )


# ---------------------------------------------------------------------------
# Hidden deprecated aliases (removed in v0.14.0)
# ---------------------------------------------------------------------------


@click.command(name="comment-edit", hidden=True)
@click.argument("comment_id")
@click.argument("content", nargs=-1)
@click.option("--content", "content_flag")
@click.pass_context
def comment_edit(
    ctx: click.Context,
    comment_id: str,
    content: tuple[str, ...],
    content_flag: str | None,
) -> None:
    """Deprecated: use ``td comment edit``."""
    click.echo(_deprecation_notice("comment-edit", "comment edit"), err=True)
    ctx.invoke(
        _comment_edit,
        comment_id=comment_id,
        content=content,
        content_flag=content_flag,
    )


@click.command(name="comment-delete", hidden=True)
@click.argument("comment_id")
@click.option("-y", "--yes", is_flag=True)
@click.pass_context
def comment_delete(ctx: click.Context, comment_id: str, yes: bool) -> None:
    """Deprecated: use ``td comment delete``."""
    click.echo(_deprecation_notice("comment-delete", "comment delete"), err=True)
    ctx.invoke(_comment_delete, comment_id=comment_id, yes=yes)
