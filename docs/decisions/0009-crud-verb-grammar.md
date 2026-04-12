# ADR-0009: CRUD verb grammar for entity commands

## Status

Accepted

## Context

PR #241 (closing issue #217) shipped 13 CRUD commands as hyphenated flat
compounds: `project-add`, `project-edit`, `project-delete`,
`project-archive`, `project-unarchive`, `section-add`, `section-edit`,
`section-delete`, `label-add`, `label-edit`, `label-delete`, `comment-edit`,
`comment-delete`. The grammar mirrored the Todoist REST API endpoint
pattern (one verb per endpoint, entity name as prefix), not user intent.

Issue #250 flagged this as a violation of ADR-0001 (*"accept what the user
means, not what the system needs"*). `td project-edit Work --name "New
Name"` reads like an API call. It is verbose, flag-heavy, and hides the
entity relationship inside a hyphenated compound. Command trees that
grow this way stop scaling gracefully as new entities are added
(`filter`, `reminder`, `notification`, `attachment`, `settings` are all
pending in the backlog).

The command set is used by two audiences: humans at terminals and AI
agents calling `td` via the `td schema` contract. The grammar decision
must serve both. Humans benefit from progressive disclosure, tab
completion, and muscle-memory alignment with other modern CLIs they
already know. Agents benefit from a cleanly nested schema and consistent
verb vocabulary across entities.

## Alternatives considered

**Option A: entity-first with ref before verb (`td project Work edit`).**
Places the entity name and target before the verb. Reads naturally in
English. Rejected because it fights Click's positional parsing model
(Click expects subcommands in a fixed position, not after a free-form
positional argument), breaks tab completion of verbs (the first
positional is a project name which has no static completion set), and
has no precedent in any comparable CLI.

**Option A2: entity-first with verb before ref (`td project edit Work`).**
Click-native: an entity group with verbs as subcommands and the ref as
the subcommand's positional argument. Matches `gh pr edit 123`,
`kubectl get pods`, `docker container inspect`. Tab completion works
cleanly: `td project <TAB>` lists verbs from the static subcommand set;
`td project edit <TAB>` dispatches to the existing `_complete_projects`
helper. `td schema` becomes a two-level nested tree.

**Option B: verb-first (`td rename project Work "New Name"`).** Flat
global verb namespace; entity type is a positional argument after the
verb. Rejected because it cross-cuts entity modules (verbs live in their
own files, entities live in theirs), loses tab-completion context (the
user selects a verb without the system knowing which entity it applies
to), and only `git` uses verb-first among comparable CLIs. `git`'s verbs
(`commit`, `rebase`, `checkout`) are primitives, not CRUD on nouns, so
its model doesn't carry over.

**Option C: smart context detection (`td edit Work --name "New Name"`).**
A top-level `edit` command that inspects `Work` and resolves it to a
project, section, label, or task by lookup. Rejected because it is
ambiguous when names collide across entity types (a project and a label
can share a name), requires a resolver-layer picker that doesn't exist,
and violates ADR-0001 §3 (*"help the user recover when things go
wrong"*) by introducing ambiguity where the user already knows which
entity they mean. The smart path is magic that fights the explicit
design principle.

**Status quo (hyphenated compounds).** The pattern we are replacing.
Rejected: the issue we are solving.

## Decision

**Use Option A2: entity-first Click groups with verb subcommands.**

```
td project add "Home improvements" --color blue
td project edit Work --name "Work & side projects"
td project delete Archive -y
td project archive Old
td project unarchive Old
td section add "Draft posts" -p Blog
td label delete urgent
td comment edit <comment_id> --content "Updated comment"
td comment delete <comment_id>
```

Four entity groups replace the 13 hyphenated flat commands:

- `project` with `add`, `edit`, `delete`, `archive`, `unarchive`, `list`
- `section` with `add`, `edit`, `delete`, `list`
- `label` with `add`, `edit`, `delete`, `list`
- `comment` with `add`, `edit`, `delete`, `list`

**Hybrid decisions that preserve high-value ergonomics:**

- **The plural list commands (`td projects`, `td sections`, `td labels`,
  `td comments`) stay as permanent flat shortcuts.** Not deprecated.
  ADR-0001 itself cites `td sections Blog` as a canonical example of
  "accept what the user means." Deprecating the plurals would regress
  against our own stated principle. `td project list` exists as a
  discoverable synonym inside the group; the plural is the shortest
  path to the most common operation.
- **`td comment <task_ref> <text>` stays as a permanent flat shortcut.**
  Implemented via `@click.group(invoke_without_command=True)` that
  inspects residual args and delegates to the `add` subcommand. The flat
  form is the primary documented usage and breaking it buys nothing.

**Deprecation window for the 13 hyphenated names:**

- **v0.13.0 (this change):** all 13 names ship as hidden aliases
  (`@click.command(hidden=True)`) that emit a one-line stderr
  deprecation notice and delegate to the new subcommand via
  `ctx.invoke(...)`. Pattern matches `quick` and `capture` in
  `src/td/cli/tasks.py:1028`.
- **v0.14.0:** hidden aliases removed.

Warning text format:

```
Note: td project-add is now td project add. The old name will be
removed in v0.14.0.
```

Emitted on every invocation (no per-session deduplication). Keeps the
shim code minimal and matches the existing alias pattern.

**Schema recursion is a required sibling change (ADR-0006 territory).**

`src/td/schema.py`'s `generate_schema` currently does not recurse into
groups. Under A2, the four new entity groups would appear as bare
entries with no subcommand information, breaking the `td schema`
contract for agents. The fix is to detect `click.Group` instances during
the walk and emit a nested `"commands"` dict on the entry, recursively
applying the same filter (hidden commands excluded at every level).

This is an **additive** schema shape change: flat commands remain
shape-identical to before. Agents walking the top level now see
`project`/`section`/`label`/`comment` as groups with `commands` keys
rather than 13 flat `project-*`/`section-*`/`label-*`/`comment-*`
entries. Called out explicitly in the CHANGELOG under `Changed`.

## Consequences

**Positive.**

- **Aligns with ADR-0001.** Entity groups read like intent, not
  endpoints. `td project edit Work --name "New"` is shorter, clearer,
  and matches how humans talk about the action.
- **Cross-CLI precedent.** `gh` (the most prominent agent-friendly CLI),
  `kubectl`, and `docker` all use entity-first verb-subcommand patterns.
  Users who know those tools transfer their muscle memory at zero cost.
- **Tab completion improves dramatically.** `td project <TAB>` lists
  verbs from the static subcommand set; `td project edit <TAB>` runs
  `_complete_projects`. No new completion machinery required.
- **Command tree scales.** Adding future CRUD operations
  (e.g. `project move`, `project clone`) has an obvious home. New
  entities (`filter`, `reminder`, `notification`) become new groups
  following the same pattern, which unblocks #212, #221, #222, #225,
  #226 and similar backlog items.
- **Schema becomes navigable.** `td schema | jq '.commands.project'`
  returns the full project verb tree for an agent to traverse, rather
  than requiring pattern-matching on flat name prefixes.
- **The hybrid preserves ergonomic wins.** Permanent plural list
  commands keep the common case short, and the permanent `td comment`
  flat shortcut preserves the primary documented usage.

**Negative.**

- **One-cycle deprecation tax.** 13 hidden alias shims live in the CLI
  for v0.13.0 → v0.14.0. The shims are mechanical wrappers (one line
  each for the notice plus a `ctx.invoke` call), and they are excluded
  from help output and schema, but they add code surface during the
  window.
- **`td schema` shape changes.** Agents that cached the flat CRUD names
  must re-fetch the schema on upgrade. This is called out in the
  CHANGELOG as an additive change per ADR-0006.
- **Documentation regeneration.** `docs/commands/organization.md` and
  the AI skill (`SKILL.md`) both need to reflect the new grammar.
  Skill regeneration is mechanical (`td skill install` walks the
  schema), but the command reference docs need manual rewriting.
- **Users may type the old name out of muscle memory.** Mitigated by
  the hidden aliases and the stderr deprecation notice. After v0.14.0
  the old names fail fast with Click's default "No such command" error,
  which is recoverable.

**Boundary preserved.** No core logic changes — the refactor is
entirely in `src/td/cli/` and `src/td/schema.py`. `core/` stays
untouched. ADR-0005 holds.

## References

- Issue #250 (the original problem)
- ADR-0001 (design principle — the rule the status quo violated)
- ADR-0002 (JSON output envelope — unchanged by this decision)
- ADR-0006 (schema as the AI contract — the additive shape change lives here)
- ADR-0008 (Click over Typer — entity groups rely on Click's command tree)
- ADR-0010 (issue triage decision framework — this ADR satisfies the
  "Needs ADR" tier requirement for any future CRUD command additions)
