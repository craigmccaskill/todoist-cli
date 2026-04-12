# Organization Commands

`td` organizes tasks around four entity types: **projects**, **sections**,
**labels**, and **comments**. Each lives under an entity-first command group
with the usual CRUD verbs (`list`, `add`, `edit`, `delete`, plus
`archive`/`unarchive` for projects). The permanent flat plural aliases
(`td projects`, `td sections`, etc.) stay as shortcuts for the common
"show me the list" case.

See [ADR-0009](../decisions/0009-crud-verb-grammar.md) for the grammar
decision.

## Projects

### td projects / td project list

List all projects.

```bash
td projects
td projects -s Work        # search by name
td project list            # identical to the plural alias
```

### td project add

Create a new project. Supports parent projects and favorites.

```bash
td project add "Home improvements"
td project add "Q2 OKRs" --parent Work
td project add "Favorites" --favorite
```

### td project edit

Rename or recolor a project. The reference is a name or ID.

```bash
td project edit Work --name "Work stuff"
td project edit Personal --color blue
```

### td project delete

Delete a project. Prompts for confirmation unless `-y` is passed.

```bash
td project delete "Old Project" -y
```

### td project archive / unarchive

```bash
td project archive "Finished Q1"
td project unarchive "Finished Q1"
```

## Sections

### td sections / td section list

List sections. Without `-p`, sections from all projects are listed
grouped by project.

```bash
td sections                # all sections, grouped by project
td sections -p Work        # sections in one project
td section list -p Work    # identical
```

### td section add

Create a new section in a project. `-p`/`--project` is required.

```bash
td section add "Draft posts" -p Blog
```

### td section edit

Rename a section. Use `-p` to scope the lookup if the same name exists
in multiple projects.

```bash
td section edit "In Progress" --name "Active" -p Work
```

### td section delete

```bash
td section delete "Old Section" -p Work -y
```

## Labels

### td labels / td label list

List all labels.

```bash
td labels
td labels -s urgent        # search by name
td label list              # identical
```

### td label add

```bash
td label add urgent
td label add work-critical
```

### td label edit

Rename or recolor a label.

```bash
td label edit urgent --name critical
td label edit low --color green
```

### td label delete

```bash
td label delete old-label -y
```

## Comments

### td comments / td comment list

List comments on a task. Accepts a row number, content match, or task ID.

```bash
td comments 1              # row number from last ls
td comments "buy milk"     # fuzzy content match
td comment list 1          # identical
```

### td comment add

Add a comment to a task. The flat shortcut `td comment <task_ref> <text>`
also works — the explicit `add` verb is discoverable, the shortcut is
the primary documented form.

```bash
td comment 1 "Picked up 2%, not whole"          # flat shortcut
td comment "buy milk" "Got oat milk instead"    # flat shortcut
td comment add 1 "Picked up 2%"                 # explicit form
```

### td comment edit

Update a comment's content. Accepts the new content as positional args
or via `--content`.

```bash
td comment edit abc123 "Updated text"
td comment edit abc123 --content "Updated text"
```

### td comment delete

```bash
td comment delete abc123 -y
```

## Deprecated names

The 13 hyphenated CRUD commands from v0.12.x still work in v0.13.0 but
print a one-line deprecation notice on stderr. They are removed in
v0.14.0 per [ADR-0009](../decisions/0009-crud-verb-grammar.md).

| Old (v0.12.x)         | New (v0.13.0+)        |
| --------------------- | --------------------- |
| `td project-add`      | `td project add`      |
| `td project-edit`     | `td project edit`     |
| `td project-delete`   | `td project delete`   |
| `td project-archive`  | `td project archive`  |
| `td project-unarchive`| `td project unarchive`|
| `td section-add`      | `td section add`      |
| `td section-edit`     | `td section edit`     |
| `td section-delete`   | `td section delete`   |
| `td label-add`        | `td label add`        |
| `td label-edit`       | `td label edit`       |
| `td label-delete`     | `td label delete`     |
| `td comment-edit`     | `td comment edit`     |
| `td comment-delete`   | `td comment delete`   |

The flat plural aliases (`td projects`, `td sections`, `td labels`,
`td comments`) and the flat comment shortcut (`td comment <task> <text>`)
are **not** deprecated. They are permanent shortcuts that match how
humans naturally ask for the list and add a note.
