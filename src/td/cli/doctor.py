"""Doctor command -- environment diagnostics."""

from __future__ import annotations

from typing import cast

import click

from td.cli.output import OutputFormatter, OutputMode

_STATUS_ICONS_RICH = {
    "pass": "[green]\u2713[/green]",
    "fail": "[red]\u2717[/red]",
    "warn": "[yellow]![/yellow]",
}

_STATUS_LABELS_PLAIN = {
    "pass": "PASS",
    "fail": "FAIL",
    "warn": "WARN",
}


def _get_formatter(ctx: click.Context) -> OutputFormatter:
    """Get the output formatter from Click context."""
    return cast(OutputFormatter, ctx.obj["formatter"])


@click.command()
@click.pass_context
def doctor(ctx: click.Context) -> None:
    """Check your environment and configuration.

    Runs diagnostic checks and reports the status of your td setup.
    Each failure includes a suggestion for how to fix it.
    """
    from td.core.doctor import run_all_checks

    formatter = _get_formatter(ctx)
    results = run_all_checks()

    if formatter.mode == OutputMode.JSON:
        formatter._json_out([r.to_dict() for r in results], "doctor")
        return

    if formatter.mode == OutputMode.PLAIN:
        for r in results:
            label = _STATUS_LABELS_PLAIN.get(r.status, r.status.upper())
            line = f"{label}\t{r.name}\t{r.detail}"
            click.echo(line)
            if r.suggestion:
                click.echo(f"\t\t{r.suggestion}")
        return

    # Rich mode
    from rich.console import Console

    console = Console(stderr=False)

    console.print()
    console.print("[bold]td doctor[/bold]")
    console.print()

    for r in results:
        icon = _STATUS_ICONS_RICH.get(r.status, "?")
        console.print(f"  {icon} [bold]{r.name}[/bold]: {r.detail}")
        if r.suggestion:
            console.print(f"      [dim]{r.suggestion}[/dim]")

    console.print()

    fail_count = sum(1 for r in results if r.status == "fail")
    warn_count = sum(1 for r in results if r.status == "warn")

    if fail_count:
        console.print(f"[red]{fail_count} issue(s) found.[/red]")
    elif warn_count:
        console.print(f"[yellow]{warn_count} warning(s).[/yellow]")
    else:
        console.print("[green]All checks passed.[/green]")
