# Organization Commands

## td projects

List all projects.

```bash
td projects
td projects -s Work    # search by name
```

## td project-add

Create a new project.

```bash
td project-add "Side Projects"
td project-add "Sub Project" --parent Work
td project-add "Favorites" --favorite
```

## td sections

List sections in a project.

```bash
td sections -p Work
```

## td section-add

Create a new section in a project.

```bash
td section-add "In Progress" -p Work
```

## td labels

List all labels.

```bash
td labels
td labels -s urgent    # search by name
```

## td label-add

Create a new label.

```bash
td label-add important
```
