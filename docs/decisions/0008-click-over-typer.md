# ADR-0008: Click over Typer

## Status

Accepted

## Context

`td` needs a Python CLI framework. The realistic options:

1. **Click.** Mature, explicit, decorator-based. Exposes the command
   tree as inspectable objects.
2. **Typer.** Built on top of Click. Uses type hints and function
   signatures to generate CLI commands with less boilerplate for
   simple cases.
3. **argparse.** Standard library. Verbose. No ecosystem for the
   richer features below.
4. **Custom.** Full control, massive maintenance burden. Unjustifiable
   for a side project.

The deciding factor is what the framework has to support *beyond*
basic argument parsing:

- Rich, JSON, and Plain output modes with uniform formatting
- Shell completion generation for bash, zsh, and fish
- A machine-readable schema of the entire command tree (ADR-0006)
- Error interception at a single chokepoint
- A custom `Group` subclass that catches and formats every exception

All of these require *owning* the command tree: walking it at runtime
to generate artifacts, intercepting method calls on the Group, and
threading a shared output formatter through every command context.
Typer abstracts the command tree behind its decorator and type-hint
machinery, which makes these walks awkward or impossible without
reaching into Typer's private internals. Click exposes the tree
directly and expects you to walk it.

## Decision

Use Click directly. Implement a custom `TdGroup(click.Group)` subclass
in `cli/__init__.py` whose `invoke()` method catches every exception,
maps API errors through `map_api_exception()`, and renders them via
`OutputFormatter`.

Do not layer Typer on top. The "less boilerplate" benefit is real but
small, and it costs direct access to the command tree that drives
schema generation (ADR-0006), shell completions, and uniform error
handling.

## Consequences

**Positive.** Every command is a `click.Command` object we can
inspect at runtime. `td schema` walks the tree directly. Shell
completions are generated from the same objects. Error handling is
uniform because `TdGroup.invoke()` is the single chokepoint for
command execution. All commands flow through `OutputFormatter` via
`ctx.obj["formatter"]`.

**Negative.** More boilerplate per command than Typer. Every flag
and argument is an explicit `@click.option` or `@click.argument`
decoration. No type-driven auto-generation from function signatures.

**Reversibility.** Adopting Typer later would require rewriting
every command decorator *and* rewriting `schema.py` to navigate
Typer's structure instead of Click's. Not a reversible decision
once commands accumulate. This ADR exists so a future refactor
does not attempt the migration without understanding what breaks.
