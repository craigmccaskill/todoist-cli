"""Comments CLI commands."""

from __future__ import annotations

import sys
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


@click.command()
@click.argument("task_ref", required=False, default=None)
@click.argument("text", nargs=-1, required=True)
@click.pass_context
def comment(ctx: click.Context, task_ref: str | None, text: tuple[str, ...]) -> None:
    """Add a comment to a task. Accepts row number, content match, or task ID.

    \b
    Examples:
      td comment 1 "Picked up 2%, not whole"
      td comment buy milk "Got oat milk instead"
    """
    api = get_client()
    fmt = _get_formatter(ctx)
    task_id = _require_task(task_ref, api)

    result = api.add_comment(content=" ".join(text), task_id=task_id)
    fmt.success(
        f"Comment added to task {task_id}",
        {"comment_id": result.id, "task_id": task_id, "content": result.content},
    )


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


@click.command(name="comment-edit")
@click.argument("comment_id")
@click.argument("content", nargs=-1)
@click.option("--content", "content_flag", help="New comment content.")
@click.pass_context
def comment_edit(
    ctx: click.Context,
    comment_id: str,
    content: tuple[str, ...],
    content_flag: str | None,
) -> None:
    """Update a comment's content. Content as positional args or --content flag.

    \b
    Examples:
      td comment-edit abc123 "Updated text"
      td comment-edit abc123 --content "Updated text"
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


@click.command(name="comment-delete")
@click.argument("comment_id")
@click.option("-y", "--yes", is_flag=True, help="Skip confirmation.")
@click.pass_context
def comment_delete(ctx: click.Context, comment_id: str, yes: bool) -> None:
    """Delete a comment by ID.

    \b
    Examples:
      td comment-delete abc123 -y
    """
    api = get_client()
    fmt = _get_formatter(ctx)

    if not yes:
        if not sys.stdout.isatty():
            raise TdValidationError(
                "Cannot confirm deletion in non-interactive mode.",
                suggestion="Use --yes flag to skip confirmation.",
            )
        if not click.confirm(f"Delete comment {comment_id}?"):
            click.echo("Aborted.")
            return

    api.delete_comment(comment_id)
    fmt.success(
        f"Deleted comment {comment_id}",
        {"comment_id": comment_id},
    )
