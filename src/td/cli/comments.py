"""Comments CLI commands."""

from __future__ import annotations

from typing import Any

import click

from td.cli.output import OutputFormatter
from td.core.client import get_client


def _get_formatter(ctx: click.Context) -> OutputFormatter:
    return ctx.obj["formatter"]  # type: ignore[no-any-return]


def _resolve_task_ref(ref: str, api: Any) -> str:
    """Import and call the shared task resolver."""
    from td.cli.tasks import _resolve_task

    return _resolve_task(ref, api)


@click.command()
@click.argument("task_ref")
@click.argument("text", nargs=-1, required=True)
@click.pass_context
def comment(ctx: click.Context, task_ref: str, text: tuple[str, ...]) -> None:
    """Add a comment to a task.

    Examples: td comment 1 "Picked up 2%, not whole"
    """
    api = get_client()
    fmt = _get_formatter(ctx)
    task_id = _resolve_task_ref(task_ref, api)

    result = api.add_comment(content=" ".join(text), task_id=task_id)
    fmt.success(
        f"Comment added to task {task_id}",
        {"comment_id": result.id, "task_id": task_id, "content": result.content},
    )


@click.command()
@click.argument("task_ref")
@click.pass_context
def comments(ctx: click.Context, task_ref: str) -> None:
    """List comments on a task.

    Examples: td comments 1 | td comments buy milk
    """
    api = get_client()
    fmt = _get_formatter(ctx)
    task_id = _resolve_task_ref(task_ref, api)

    all_comments = [c for page in api.get_comments(task_id=task_id) for c in page]

    if fmt.mode.value == "json":
        fmt._json_out([c.to_dict() for c in all_comments], "comment_list")
    elif fmt.mode.value == "plain":
        click.echo("ID\tCONTENT\tPOSTED")
        for c in all_comments:
            click.echo(f"{c.id}\t{c.content}\t{c.posted_at}")
    else:
        assert fmt._console is not None
        from rich.table import Table

        table = Table(title="Comments", show_lines=False)
        table.add_column("Content", style="bold")
        table.add_column("Posted", style="dim")
        table.add_column("ID", style="dim")

        for c in all_comments:
            table.add_row(c.content, str(c.posted_at), c.id)

        fmt._console.print(table)
