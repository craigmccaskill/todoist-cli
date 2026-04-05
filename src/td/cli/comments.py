"""Comments CLI commands."""

from __future__ import annotations

from typing import Any, cast

import click

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
    """Add a comment to a task.

    Examples: td comment 1 "Picked up 2%, not whole"
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
    """List comments on a task.

    Examples: td comments 1 | td comments buy milk
    """
    api = get_client()
    fmt = _get_formatter(ctx)
    task_id = _require_task(task_ref, api)

    all_comments = [c for page in api.get_comments(task_id=task_id) for c in page]
    fmt.comment_list(all_comments)
