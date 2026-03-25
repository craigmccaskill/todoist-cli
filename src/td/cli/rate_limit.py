"""Rate limit CLI command."""

from __future__ import annotations

import click

from td.cli.output import OutputFormatter
from td.core.rate_limit import load_rate_limit_cache


def _get_formatter(ctx: click.Context) -> OutputFormatter:
    return ctx.obj["formatter"]  # type: ignore[no-any-return]


@click.command(name="rate-limit")
@click.pass_context
def rate_limit(ctx: click.Context) -> None:
    """Show current API rate limit status from cached response headers."""
    fmt = _get_formatter(ctx)
    data = load_rate_limit_cache()

    remaining = data["remaining"]
    limit = data["limit"]

    if remaining is None:
        fmt.success("No rate limit data cached yet. Run any command first.")
        return

    assert limit is not None
    pct = (remaining / limit * 100) if limit > 0 else 0

    if fmt.mode.value == "json":
        fmt._json_out(
            {"remaining": remaining, "limit": limit, "percent_remaining": round(pct, 1)},
            "rate_limit",
        )
    elif fmt.mode.value == "plain":
        click.echo(f"{remaining}\t{limit}\t{pct:.1f}%")
    else:
        assert fmt._console is not None
        style = "green" if pct > 50 else ("yellow" if pct > 20 else "red bold")
        fmt._console.print(
            f"API rate limit: [{style}]{remaining}/{limit}[/{style}] ({pct:.0f}% remaining)"
        )
