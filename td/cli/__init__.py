"""CLI entrypoint and Click group."""

from __future__ import annotations

import sys

import click

from td import __version__
from td.cli.errors import TdError, handle_error, map_api_exception
from td.cli.output import OutputFormatter, OutputMode, resolve_output_mode
from td.core.config import load_config


class TdGroup(click.Group):
    """Custom Click group with structured error handling."""

    def invoke(self, ctx: click.Context) -> None:
        try:
            super().invoke(ctx)
        except TdError as e:
            mode = self._get_mode(ctx)
            handle_error(e, mode)
            sys.exit(1)
        except Exception as e:
            if isinstance(e, (click.ClickException, SystemExit)):
                raise
            td_error = map_api_exception(e)
            mode = self._get_mode(ctx)
            handle_error(td_error, mode)
            sys.exit(1)

    @staticmethod
    def _get_mode(ctx: click.Context) -> OutputMode:
        try:
            formatter = ctx.obj.get("formatter") if ctx.obj else None
            if formatter:
                return formatter.mode  # type: ignore[no-any-return]
        except Exception:
            pass
        return OutputMode.JSON


@click.group(cls=TdGroup, context_settings={"help_option_names": ["-h", "--help"]})
@click.option("--json", "output_json", is_flag=True, help="Force JSON output.")
@click.option("--plain", is_flag=True, help="Force plain text output (no color).")
@click.version_option(version=__version__, prog_name="td")
@click.pass_context
def cli(ctx: click.Context, output_json: bool, plain: bool) -> None:
    """td — AI-native Todoist CLI."""
    ctx.ensure_object(dict)
    config = load_config()
    mode = resolve_output_mode(
        output_json, plain, color=config.color, default_format=config.default_format
    )
    ctx.obj["formatter"] = OutputFormatter(mode)


# Register subcommands (imported here to avoid circular imports)
def _register_commands() -> None:
    from td.cli.config_cmd import completions, init
    from td.cli.labels import labels
    from td.cli.projects import project_add, projects
    from td.cli.schema_cmd import schema
    from td.cli.sections import sections
    from td.cli.tasks import (
        add,
        delete,
        done,
        edit,
        focus,
        inbox,
        log,
        ls,
        next_task,
        quick,
        today,
        undo,
    )

    cli.add_command(init)
    cli.add_command(completions)
    cli.add_command(schema)
    cli.add_command(add)
    cli.add_command(ls)
    cli.add_command(inbox)
    cli.add_command(today)
    cli.add_command(next_task)
    cli.add_command(log)
    cli.add_command(focus)
    cli.add_command(done)
    cli.add_command(edit)
    cli.add_command(delete)
    cli.add_command(quick)
    cli.add_command(undo)
    cli.add_command(projects)
    cli.add_command(project_add)
    cli.add_command(sections)
    cli.add_command(labels)


_register_commands()


def main() -> None:
    """Entrypoint for the `td` console script."""
    cli()
