# ADR-0010: Issue triage decision framework

## Status

Accepted

## Context

The board conventions documented in `CONTRIBUTING.md` (`Status`,
`Tier`, `Priority`, `Size`, `Theme`) and the mandatory-at-triage rule
for `Tier` / `Size` / `Priority` require every new issue to be
classified consistently. Without an explicit rubric:

1. Classification drifts with the triage session's mood.
2. The boundary between `Standard` and `Needs ADR` becomes fuzzy,
   and issues like #250 slip through as `Standard` when they are
   actually `Needs ADR`.
3. Size estimation varies depending on what was worked on last.
4. Priority bumps happen reactively instead of from clear criteria.
5. Re-triage (a planned pass over existing open items) has no
   baseline to apply.

The foundation PR and the board-conventions PR documented the
fields and their meanings. This ADR documents the *process* for
classifying an issue into those fields: a rubric walked during
triage.

Two formats were considered:

1. **Flowchart** (if-then decision tree that mechanically produces a
   classification). More enforceable, but brittle at edge cases and
   harder to extend.
2. **Checklist** (a set of considerations that guides judgment but
   leaves interpretation to the triager). More flexible, relies on
   discipline. Easier to extend as new edge cases surface.

For a solo maintainer, the checklist is more appropriate. The
triager and the rubric author are the same person, so mechanical
enforcement buys less than it would on a team.

## Decision

Triage uses a **checklist-style rubric**, walked for every issue
leaving the `Needs triage` state. The rubric lives in this ADR,
not in a command, skill, or GitHub Action. Maintainer tooling is
out of scope for the public `td` CLI (see ADR-0001's CLI surface
boundary). If automation is ever wanted, it lives in a Claude
skill or a maintainer script under `.github/` or `scripts/`, not
as a `td` command.

### The rubric

#### Step 1: Classify `Tier`

Walk the list top to bottom. First match wins.

- [ ] Is this a typo, one-line fix, dependency bump, CI tweak, or
      documentation-only change with no semantic impact?
      → **`Tier: Trivial`**. Skip `Size` and `Priority` if obvious,
      otherwise continue.

- [ ] Is this a research question (*"is X viable?"*, *"what's the
      right approach for Y?"*) rather than a known task?
      → **`Tier: Exploratory`**. Scope the investigation as the
      deliverable, not the outcome. Re-triage after the investigation
      produces a proposal.

- [ ] Does this change introduce or modify any of:
      - Command grammar (new top-level command, renamed command,
        new subcommand structure)
      - JSON output envelope (ADR-0002) or a new `type` value
      - An architectural invariant (`core/` / `cli/` boundary from
        ADR-0005, schema contract from ADR-0006, task resolution
        order from ADR-0004)
      - Interpretation of the design principle from ADR-0001

      → **`Tier: Needs ADR`**. Draft a proposed ADR before the PR
      opens.

- [ ] Default:
      → **`Tier: Standard`**. A 5-item pre-work comment is required
      on the issue before a branch exists.

#### Step 2: Estimate `Size`

| Value | Meaning |
|---|---|
| `S` | Small. A few hours at most. Single file or trivial multi-file. Under 50 LoC. |
| `M` | Medium. Most of a day. Multiple files in one module. Under 200 LoC. |
| `L` | Large. Multiple days. Cross-module or large refactor. Over 200 LoC. |

**Size triggers.** Any change over 200 LoC or touching more than
three modules cannot be classified as `Trivial`, and must at
least be `Standard`. The size trigger also forces the question
*"is this actually `Needs ADR`?"*

**Size uncertainty.** If you genuinely cannot estimate, default to
`M` and revise in the pre-work comment or during investigation.

#### Step 3: Set `Priority`

| Value | Meaning |
|---|---|
| `P0` | Literal emergency. Production broken or security issue live. Drop everything. |
| `P1` | Important. Pick up soon, before the normal rotation. |
| `P2` | Normal. Default for new work. Most issues. |
| `P3` | Someday. Backlog of ideas without deadlines. |

If you're tempted to pick `P1` because the issue is recent or
interesting, resist. `P1` means *"should ship in the next
milestone"*, not *"I remember filing this and I care about it."*

#### Step 4: Check dependencies

- Read the issue body for `Blocks:` / `Blocked by:` lines (see
  ADR-0011 for the dependency tracking convention)
- If the issue is part of an epic, check the parent issue's task
  list
- If dependencies exist, note them so milestone planning can
  sequence the work correctly

#### Step 5: Set `Theme` and labels

`Theme` and labels are strongly encouraged but not mandatory at
triage. Pick them if obvious, leave unset if not.

### Worked examples

**Example 1: Typo in a help string**
- `Tier`: `Trivial` (typo with no semantic impact)
- `Size`: `S` (one line)
- `Priority`: `P3` (nothing breaks)
- Dependencies: none
- Ready to merge without a pre-work comment

**Example 2: Add a `--output ndjson` flag to `td ls`**
- `Tier`: `Needs ADR` (new output mode, touches the envelope
  contract from ADR-0002)
- `Size`: `M` (multiple files, new formatter logic)
- `Priority`: `P2` (default)
- Dependencies: none
- Pre-work: propose an ADR for the NDJSON envelope shape, then
  implement

**Example 3: "Figure out how to support MCP"**
- `Tier`: `Exploratory` (research question, not a known task)
- `Size`: unknown at triage time (deferred until after the
  investigation scopes the work)
- `Priority`: `P1` (vision-critical)
- Dependencies: `Blocks:` several future MCP items
- Pre-work: scope the investigation, timebox, produce a follow-up
  issue or proposed ADR based on findings

**Example 4: "Rename 10 CRUD commands to a new verb grammar"**
- First pass: `Tier: Standard` (clear task, mechanical refactor)
- `Size: L` (over 200 LoC, more than three modules)
- Size trigger forces the question: is this actually `Needs ADR`?
- After thinking: yes, because the rename *is* a command grammar
  change → **re-classify to `Needs ADR`**
- Pre-work: write the proposed grammar ADR (this is literally what
  #250 will produce via ADR-0009)

### Edge cases

- **Issue spans multiple Tiers.** A `Standard` refactor that
  includes one `Needs ADR` sub-decision should be decomposed into
  two issues, one per Tier. Do not classify the parent as the
  highest Tier and hope the rest comes along.
- **Size is genuinely unknown.** Start at `M`, note the uncertainty
  in the pre-work comment, revise during investigation.
- **Classification changes mid-work.** Update the issue's `Tier` on
  the board. If it went from `Standard` to `Needs ADR` after
  discovering the design implications, stop coding and write the
  ADR first.
- **"Do this thing, and also this related thing."** These are two
  issues, not one. Split them during triage.

### References

- Field definitions: `CONTRIBUTING.md` → *Project board conventions*
- Dependency tracking mechanism: ADR-0011
- CLI surface boundary (why this is a doc, not a command): ADR-0001

## Consequences

**Positive.** Triage becomes repeatable. Same decisions in the same
contexts yield the same classifications. The rubric is citable in
issue comments (*"classified as Needs ADR per ADR-0010 Step 1
bullet 3"*). New contributors have a clear starting point for
classifying their own issues. Re-triage has a baseline to apply
across existing items. Checklist format is extensible: new
considerations can be added without restructuring the whole rubric.

**Negative.** A rubric only helps if the triager actually opens it
during triage. Enforcement is discipline, not mechanical. Step 1's
"first match wins" ordering is opinionated and may produce the
wrong classification for genuinely ambiguous work. Worked examples
will become stale as the project evolves and need occasional
refreshing. Mis-classification only surfaces when the downstream
pre-work feels wrong (for example, you end up writing an ADR for
work that was tagged `Standard`).

**Discipline.** Open this ADR at the start of every triage session.
If the rubric produces a classification that feels wrong, stop and
reconsider. Either the rubric is wrong (write a superseding ADR) or
the issue is wrong (rewrite the issue to match what you actually
want). Do not override the rubric silently.
