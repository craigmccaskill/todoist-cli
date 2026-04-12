# Architecture Decision Records

This directory contains Architecture Decision Records (ADRs) for `td`.
Each ADR captures a single design decision in one page: the context
that forced it, the decision we made, and the consequences we accept.

## Why ADRs

Design decisions that live only in code comments or commit messages
decay as the project grows. New contributors (human or AI agent) have
to reverse-engineer *why* a thing is the way it is from *how* it is.
ADRs give those decisions a durable, citeable home so the reasoning
compounds rather than evaporating.

## How to use this directory

**Reading.** Open the numbered file that matches your question. Each
ADR is one page. If you need more, the ADR will tell you where.

**Citing.** Reference ADRs by number in PR descriptions, issues, and
commit messages: *"implements ADR-0003"* or *"this diverges from
ADR-0001, see ADR-0009."*

**Writing.** Before adding a new ADR, read the *Architecture Decision
Records* section in the project's `CONTRIBUTING.md` (repo root) for
the full process. Short version:

1. Copy an existing ADR as a template
2. Number it with the next available `NNNN` prefix
3. Set status to `Proposed`
4. Fill in Context, Decision, Consequences
5. Link it from this README's index
6. After review, flip status to `Accepted`

**Scope.** ADRs are for architectural and design decisions, not
tactical changes. The test: *would a new contributor (or agent) need
to understand this to make a good change?* If no, use a code comment
or commit message.

**Immutability.** Once an ADR reaches `Accepted`, its body is never
edited. If reality changes, write a new ADR that supersedes the old
one, and mark the old one `Superseded by ADR-NNNN`. This preserves the
history of thinking, not just the history of code.

**One page.** If an ADR runs longer than a page, it's a proposal
document, not a decision. Trim before accepting.

## Index

| #    | Title                                                     | Status   |
|------|-----------------------------------------------------------|----------|
| [0001](0001-design-principle.md) | Design Principle                   | Accepted |
| [0002](0002-output-envelope.md) | JSON Output Envelope                | Accepted |
| [0003](0003-priority-mapping.md) | Priority Number Mapping            | Accepted |
| [0004](0004-task-ref-resolution.md) | Task Reference Resolution Order | Accepted |
| [0005](0005-core-cli-boundary.md) | Architectural Import Boundary    | Accepted |
| [0006](0006-schema-as-ai-contract.md) | Schema as the AI Contract    | Accepted |
| [0007](0007-row-number-cache-ttl.md) | Row-Number Cache TTLs         | Accepted |
| [0008](0008-click-over-typer.md) | Click over Typer                   | Accepted |
| [0009](0009-crud-verb-grammar.md) | CRUD verb grammar for entity commands | Accepted |
| [0010](0010-triage-framework.md) | Issue triage decision framework    | Accepted |
| [0011](0011-dependency-tracking.md) | Dependency tracking between issues | Accepted |
