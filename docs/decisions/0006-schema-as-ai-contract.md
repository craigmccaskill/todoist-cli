# ADR-0006: Schema as the AI Contract

## Status

Accepted

## Context

`td` is built for AI agents as a first-class audience, not as an
afterthought. An agent integrating with `td` needs to know:

1. What commands exist
2. What arguments and flags each command accepts
3. What output shapes to expect (the `type` values from ADR-0002)
4. How errors are structured

Without a machine-readable answer to these questions, every agent
integration starts from trial-and-error or out-of-date documentation.
The more commands we add, the worse it gets.

Two mechanisms were considered:

1. **Handwritten manifest.** A separate YAML or JSON file listing
   commands and arguments. Pros: explicit, reviewable. Cons: drifts
   from the real command definitions the moment someone adds a flag
   without updating the manifest. Drift is silent and cumulative.
2. **Introspected schema.** Walk the Click command tree at runtime
   and emit JSON describing every command, argument, flag, and help
   string. Pros: always in sync with the code because it *is* the
   code. Cons: requires ownership of the command tree, which means
   Click (see ADR-0008) rather than Typer.

The introspected approach cannot drift from the code. The handwritten
approach will drift the first time the reviewer is tired.

## Decision

`td schema` is the canonical AI contract. It walks the Click command
tree rooted at `cli/__init__.py` and emits a JSON document describing
every command, every argument, every flag, every help string, and
the JSON envelope format from ADR-0002.

Implementation lives in `src/td/schema.py` and
`src/td/cli/schema_cmd.py`.

The output of `td schema` is the contract. An agent reads it once at
integration time, caches the structure, and uses it to generate
command invocations. Future releases may add commands, flags, or
`type` values, but breaking changes to the schema *structure*
(renaming fields, changing types, dropping commands) require a
superseding ADR and a major version bump once `td` reaches 1.0.

This decision is also why ADR-0008 chose Click over Typer: Click
exposes the command tree directly and the walk is straightforward,
while Typer's decorator abstraction obscures it.

## Consequences

**Positive.** Agents have a single, always-current source of truth
for `td`'s capabilities. Adding a new command automatically surfaces
it in `td schema` output with no manifest update required. The
schema is testable: a test in the suite verifies that every
registered command appears in the schema output.

**Negative.** The schema structure is a contract. Changes that
rename fields, restructure sections, or drop commands are
user-visible breaks. This is a load-bearing constraint during
refactors that's easy to forget. Mitigation: schema-shape changes
are called out explicitly in CHANGELOG `Changed` entries, and any
such change in `td schema` output requires a review pass against
this ADR and any relevant newer ADRs.

**Discipline.** When a new command is added, the schema test must
pass. If it doesn't, the new command's registration in `cli/__init__.py`
is wrong, not the schema code.
