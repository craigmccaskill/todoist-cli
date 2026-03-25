# td — Command Examples

Auto-generated example output for every td command.


## Global Help

### `td --help`

```
$ td --help
Usage: td [OPTIONS] COMMAND [ARGS]...

  td — AI-native Todoist CLI.

Options:
  --json      Force JSON output.
  --plain     Force plain text output (no color).
  --debug     Show API request details on stderr.
  --version   Show the version and exit.
  -h, --help  Show this message and exit.

Commands:
  add          Create a new task.
  capture      Quick-capture to inbox — no parsing, no flags, minimal output.
  comment      Add a comment to a task.
  comments     List comments on a task.
  completions  Generate shell completion script.
  delete       Delete a task.
  done         Complete a task.
  edit         Update a task.
  focus        Focus on a single project — deep work mode.
  inbox        Show unprocessed inbox tasks.
  init         Set up authentication and configuration.
  label-add    Create a new label.
  labels       List all labels.
  log          Show completed tasks — your end-of-day review.
  ls           List tasks.
  move         Move a task to a different project.
  next         Show your highest priority task — what to work on now.
  project-add  Create a new project.
  projects     List all projects.
  quick        Natural language task creation.
  rate-limit   Show current API rate limit status from cached response...
  review       Interactive inbox review — process tasks one by one.
  schema       Output full capability manifest as JSON.
  search       Search tasks by keyword across all projects.
  section-add  Create a new section in a project.
  sections     List sections in a project.
  show         View full task details.
  today        Show tasks due today and overdue — your morning dashboard.
  undo         Reopen a completed task.
```


## Version

### `td --version`

```
$ td --version
td, version 0.7.0-alpha
```


## Task Commands

### `td --json ls`

List all tasks (JSON mode).

```
$ td --json ls
{
  "ok": true,
  "type": "task_list",
  "data": [
    {
      "id": "8bx9a0c2",
      "content": "Review PR for auth module",
      "priority": 4,
      "labels": [
        "work",
        "code-review"
      ],
      "project_id": "220474322",
      "description": "",
      "due": {
        "string": "Mar 25",
        "date": "2026-03-25"
      },
      "project_name": "Inbox"
    },
    {
      "id": "7ky3m1f9",
      "content": "Buy groceries",
      "priority": 1,
      "labels": [
        "errands"
      ],
      "project_id": "220474322",
      "description": "",
      "due": {
        "string": "Mar 26",
        "date": "2026-03-26"
      },
      "project_name": "Inbox"
    }
  ]
}
```

### `td --plain ls`

List all tasks (plain mode).

```
$ td --plain ls
#	ID	CONTENT	PROJECT	DUE	PRIORITY	LABELS
1	8bx9a0c2	Review PR for auth module	Inbox	2026-03-25	p1	work,code-review
2	7ky3m1f9	Buy groceries	Inbox	2026-03-26	p4	errands
```

### `td --json ls -f "today & #Work"`

List tasks with a Todoist filter query.

```
$ td --json ls -f "today & #Work"
{
  "ok": true,
  "type": "task_list",
  "data": [
    {
      "id": "8bx9a0c2",
      "content": "Review PR for auth module",
      "priority": 4,
      "labels": [
        "work",
        "code-review"
      ],
      "project_id": "220474322",
      "description": "",
      "due": {
        "string": "Mar 25",
        "date": "2026-03-25"
      },
      "project_name": "Inbox"
    },
    {
      "id": "7ky3m1f9",
      "content": "Buy groceries",
      "priority": 1,
      "labels": [
        "errands"
      ],
      "project_id": "220474322",
      "description": "",
      "due": {
        "string": "Mar 26",
        "date": "2026-03-26"
      },
      "project_name": "Inbox"
    }
  ]
}
```

### `td --json inbox`

Show inbox tasks.

```
$ td --json inbox
{
  "ok": true,
  "type": "task_list",
  "data": [
    {
      "id": "8bx9a0c2",
      "content": "Review PR for auth module",
      "priority": 4,
      "labels": [
        "work",
        "code-review"
      ],
      "project_id": "220474322",
      "description": "",
      "due": {
        "string": "Mar 25",
        "date": "2026-03-25"
      },
      "project_name": "Inbox"
    },
    {
      "id": "4np6r2d5",
      "content": "Write blog post draft",
      "priority": 3,
      "labels": [
        "writing"
      ],
      "project_id": "220474322",
      "description": "",
      "due": {
        "string": "Mar 28",
        "date": "2026-03-28"
      }
    },
    {
      "id": "1aq8s4g7",
      "content": "Schedule dentist appointment",
      "priority": 2,
      "labels": [],
      "project_id": "220474322",
      "description": "",
      "due": null
    },
    {
      "id": "7ky3m1f9",
      "content": "Buy groceries",
      "priority": 1,
      "labels": [
        "errands"
      ],
      "project_id": "220474322",
      "description": "",
      "due": {
        "string": "Mar 26",
        "date": "2026-03-26"
      },
      "project_name": "Inbox"
    }
  ]
}
```

### `td --json add "Review PR for auth module" -p Work --priority 1 -d tomorrow -l work -l code-review`

Create a task with project, priority, due date, and labels.

```
$ td --json add "Review PR for auth module" -p Work --priority 1 -d tomorrow -l work -l code-review
{
  "ok": true,
  "type": "task_created",
  "data": {
    "id": "8bx9a0c2",
    "content": "Review PR for auth module",
    "priority": 4,
    "labels": [
      "work",
      "code-review"
    ],
    "project_id": "220474322",
    "description": "",
    "due": {
      "string": "Mar 25",
      "date": "2026-03-25"
    },
    "project_name": "Inbox",
    "created": true
  }
}
```

### `td --json add "Review PR for auth module" --idempotent`

Idempotent add — returns existing task if content matches.

```
$ td --json add "Review PR for auth module" --idempotent
{
  "ok": true,
  "type": "task_created",
  "data": {
    "id": "8bx9a0c2",
    "content": "Review PR for auth module",
    "priority": 4,
    "labels": [
      "work",
      "code-review"
    ],
    "project_id": "220474322",
    "description": "",
    "due": {
      "string": "Mar 25",
      "date": "2026-03-25"
    },
    "project_name": "Inbox",
    "created": false
  }
}
```

### `td --json quick "Buy groceries tomorrow p2 #errands"`

Natural language task creation.

```
$ td --json quick "Buy groceries tomorrow p2 #errands"
{
  "ok": true,
  "type": "task_created",
  "data": {
    "id": "7ky3m1f9",
    "content": "Buy groceries",
    "priority": 1,
    "labels": [
      "errands"
    ],
    "project_id": "220474322",
    "description": "",
    "due": {
      "string": "Mar 26",
      "date": "2026-03-26"
    },
    "project_name": "Inbox",
    "created": true
  }
}
```

### `td --json capture Call dentist about appointment`

Quick-capture to inbox — no parsing, no flags.

```
$ td --json capture Call dentist about appointment
{
  "ok": true,
  "type": "success",
  "data": {
    "task_id": "8bx9a0c2"
  }
}
```

### `td --json done 8bx9a0c2`

Complete a task.

```
$ td --json done 8bx9a0c2
{
  "ok": true,
  "type": "success",
  "data": {
    "task_id": "8bx9a0c2"
  }
}
```

### `td --json undo 8bx9a0c2`

Reopen a completed task.

```
$ td --json undo 8bx9a0c2
{
  "ok": true,
  "type": "success",
  "data": {
    "task_id": "8bx9a0c2"
  }
}
```

### `td --json edit 8bx9a0c2 --content "Review PR for auth module (updated)" --priority 2`

Update a task.

```
$ td --json edit 8bx9a0c2 --content "Review PR for auth module (updated)" --priority 2
{
  "ok": true,
  "type": "task",
  "data": {
    "id": "8bx9a0c2",
    "content": "Review PR for auth module",
    "priority": 4,
    "labels": [
      "work",
      "code-review"
    ],
    "project_id": "220474322",
    "description": "",
    "due": {
      "string": "Mar 25",
      "date": "2026-03-25"
    },
    "project_name": "Inbox"
  }
}
```

### `td --json show 8bx9a0c2`

View full task details.

```
$ td --json show 8bx9a0c2
{
  "ok": true,
  "type": "task",
  "data": {
    "id": "8bx9a0c2",
    "content": "Review PR for auth module",
    "priority": 4,
    "labels": [
      "work",
      "code-review"
    ],
    "project_id": "220474322",
    "description": "",
    "due": {
      "string": "Mar 25",
      "date": "2026-03-25"
    },
    "project_name": "Inbox"
  }
}
```

### `td --json move 8bx9a0c2 -p "Work"`

Move a task to a different project.

```
$ td --json move 8bx9a0c2 -p "Work"
{
  "ok": true,
  "type": "success",
  "data": {
    "task_id": "8bx9a0c2",
    "project_id": "220474323",
    "project_name": "Work"
  }
}
```

### `td --json search review`

Search tasks by keyword.

```
$ td --json search review
{
  "ok": true,
  "type": "task_list",
  "data": [
    {
      "id": "8bx9a0c2",
      "content": "Review PR for auth module",
      "priority": 4,
      "labels": [
        "work",
        "code-review"
      ],
      "project_id": "220474322",
      "description": "",
      "due": {
        "string": "Mar 25",
        "date": "2026-03-25"
      },
      "project_name": "Inbox"
    },
    {
      "id": "7ky3m1f9",
      "content": "Buy groceries",
      "priority": 1,
      "labels": [
        "errands"
      ],
      "project_id": "220474322",
      "description": "",
      "due": {
        "string": "Mar 26",
        "date": "2026-03-26"
      },
      "project_name": "Inbox"
    }
  ]
}
```

### `td --json delete 8bx9a0c2 --yes`

Delete a task (with --yes to skip confirmation).

```
$ td --json delete 8bx9a0c2 --yes
{
  "ok": true,
  "type": "success",
  "data": {
    "task_id": "8bx9a0c2"
  }
}
```

### `td --json comment 8bx9a0c2 "Picked up 2%, not whole"`

Add a comment to a task.

```
$ td --json comment 8bx9a0c2 "Picked up 2%, not whole"
{
  "ok": true,
  "type": "success",
  "data": {
    "comment_id": "c1",
    "task_id": "8bx9a0c2",
    "content": "Picked up 2%, not whole"
  }
}
```

### `td --json comments 8bx9a0c2`

List comments on a task.

```
$ td --json comments 8bx9a0c2
{
  "ok": true,
  "type": "comment_list",
  "data": [
    {
      "id": "c1",
      "content": "Picked up 2%, not whole",
      "posted_at": "2026-03-25T10:30:00Z"
    }
  ]
}
```


## Workflow Commands

### `td --json today`

Show tasks due today and overdue — your morning dashboard.

```
$ td --json today
{
  "ok": true,
  "type": "task_list",
  "data": [
    {
      "id": "8bx9a0c2",
      "content": "Review PR for auth module",
      "priority": 4,
      "labels": [
        "work",
        "code-review"
      ],
      "project_id": "220474322",
      "description": "",
      "due": {
        "string": "Mar 25",
        "date": "2026-03-25"
      },
      "project_name": "Inbox"
    },
    {
      "id": "7ky3m1f9",
      "content": "Buy groceries",
      "priority": 1,
      "labels": [
        "errands"
      ],
      "project_id": "220474322",
      "description": "",
      "due": {
        "string": "Mar 26",
        "date": "2026-03-26"
      },
      "project_name": "Inbox"
    }
  ]
}
```

### `td --json next`

Show your highest priority task.

```
$ td --json next
{
  "ok": true,
  "type": "task",
  "data": {
    "id": "8bx9a0c2",
    "content": "Review PR for auth module",
    "priority": 4,
    "labels": [
      "work",
      "code-review"
    ],
    "project_id": "220474322",
    "description": "",
    "due": {
      "string": "Mar 25",
      "date": "2026-03-25"
    },
    "project_name": "Inbox"
  }
}
```

### `td --json focus "Work"`

Focus on a single project.

```
$ td --json focus "Work"
{
  "ok": true,
  "type": "task_list",
  "data": [
    {
      "id": "8bx9a0c2",
      "content": "Review PR for auth module",
      "priority": 4,
      "labels": [
        "work",
        "code-review"
      ],
      "project_id": "220474322",
      "description": "",
      "due": {
        "string": "Mar 25",
        "date": "2026-03-25"
      },
      "project_name": "Inbox"
    },
    {
      "id": "4np6r2d5",
      "content": "Write blog post draft",
      "priority": 3,
      "labels": [
        "writing"
      ],
      "project_id": "220474322",
      "description": "",
      "due": {
        "string": "Mar 28",
        "date": "2026-03-28"
      }
    },
    {
      "id": "1aq8s4g7",
      "content": "Schedule dentist appointment",
      "priority": 2,
      "labels": [],
      "project_id": "220474322",
      "description": "",
      "due": null
    },
    {
      "id": "7ky3m1f9",
      "content": "Buy groceries",
      "priority": 1,
      "labels": [
        "errands"
      ],
      "project_id": "220474322",
      "description": "",
      "due": {
        "string": "Mar 26",
        "date": "2026-03-26"
      },
      "project_name": "Inbox"
    }
  ]
}
```


## Organization Commands

### `td --json projects`

List all projects.

```
$ td --json projects
{
  "ok": true,
  "type": "project_list",
  "data": [
    {
      "id": "220474322",
      "name": "Inbox",
      "is_favorite": false
    },
    {
      "id": "220474323",
      "name": "Work",
      "is_favorite": true
    },
    {
      "id": "220474324",
      "name": "Personal",
      "is_favorite": false
    },
    {
      "id": "220474325",
      "name": "Side Projects",
      "is_favorite": false
    }
  ]
}
```

### `td --plain projects`

List projects (plain mode).

```
$ td --plain projects
ID	NAME
220474322	Inbox
220474323	Work
220474324	Personal
220474325	Side Projects
```

### `td --json projects -s "Work"`

Search projects.

```
$ td --json projects -s "Work"
{
  "ok": true,
  "type": "project_list",
  "data": [
    {
      "id": "220474323",
      "name": "Work",
      "is_favorite": true
    }
  ]
}
```

### `td --json project-add "Side Projects"`

Create a new project.

```
$ td --json project-add "Side Projects"
{
  "ok": true,
  "type": "project_created",
  "data": {
    "id": "220474323",
    "name": "Work",
    "is_favorite": true,
    "created": true
  }
}
```

### `td --json sections -p "Work"`

List sections in a project.

```
$ td --json sections -p "Work"
{
  "ok": true,
  "type": "section_list",
  "data": [
    {
      "id": "s1",
      "name": "Backlog"
    },
    {
      "id": "s2",
      "name": "In Progress"
    },
    {
      "id": "s3",
      "name": "Done"
    }
  ]
}
```

### `td --json section-add "In Progress" -p "Work"`

Create a new section in a project.

```
$ td --json section-add "In Progress" -p "Work"
{
  "ok": true,
  "type": "section_created",
  "data": {
    "id": "s2",
    "name": "In Progress",
    "created": true
  }
}
```

### `td --json labels`

List all labels.

```
$ td --json labels
{
  "ok": true,
  "type": "label_list",
  "data": [
    {
      "id": "lbl1",
      "name": "urgent"
    },
    {
      "id": "lbl2",
      "name": "work"
    },
    {
      "id": "lbl3",
      "name": "errands"
    },
    {
      "id": "lbl4",
      "name": "writing"
    },
    {
      "id": "lbl5",
      "name": "code-review"
    }
  ]
}
```

### `td --plain labels`

List labels (plain mode).

```
$ td --plain labels
ID	NAME
lbl1	urgent
lbl2	work
lbl3	errands
lbl4	writing
lbl5	code-review
```

### `td --json label-add urgent`

Create a new label.

```
$ td --json label-add urgent
{
  "ok": true,
  "type": "label_created",
  "data": {
    "id": "lbl1",
    "name": "urgent",
    "created": true
  }
}
```


## AI-Native Commands

### `td schema`

Output the full capability manifest. Agents call this once to learn everything.

```
$ td schema
{
  "name": "td",
  "version": "0.7.0-alpha",
  "description": "AI-native Todoist CLI",
  "commands": {
    "add": {
      "description": "Create a new task. Reads from stdin if no content argument.",
      "arguments": [
        {
          "name": "content",
          "type": "text",
          "required": false
        }
      ],
      "options": [
        {
          "name": "project_name",
          "type": "text",
          "required": false,
          "flags": [
            "-p",
            "--project"
          ],
          "help": "Project name or ID.",
          "is_flag": false
        },
        {
          "name": "priority",
          "type": "int(1-4)",
          "required": false,
          "flags": [
            "--priority"
          ],
          "help": "Priority: 1=urgent, 2=high, 3=medium, 4=low.",
          "is_flag": false
        },
        {
          "name": "due",
          "type": "text",
          "required": false,
          "flags": [
            "-d",
            "--due"
          ],
          "help": "Due date (e.g., 'tomorrow', '2026-04-01').",
          "is_flag": false
        },
        {
          "name": "labels",
          "type": "text",
          "required": false,
          "flags": [
            "-l",
            "--label"
          ],
          "help": "Label (repeatable).",
          "is_flag": false
        },
        {
          "name": "description",
          "type": "text",
          "required": false,
          "flags": [
            "--desc"
          ],
          "help": "Task description.",
          "is_flag": false
        },
        {
          "name": "section_name",
          "type": "text",
          "required": false,
          "flags": [
            "-s",
            "--section"
          ],
          "help": "Section name (requires --project).",
          "is_flag": false
        },
        {
          "name": "idempotent",
          "type": "boolean",
          "required": false,
          "flags": [
            "--idempotent"
          ],
          "help": "Skip if identical task already exists.",
          "is_flag": true,
          "default": false
        }
      ]
    },
    "capture": {
      "description": "Quick-capture to inbox \u2014 no parsing, no flags, minimal output.\n\n    Example: td capture call dentist about appointment\n    ",
      "arguments": [
        {
          "name": "text",
          "type": "text",
          "required": true
        }
      ],
      "options": []
    },
    "comment": {
      "description": "Add a comment to a task.\n\n    Examples: td comment 1 \"Picked up 2%, not whole\"\n    ",
      "arguments": [
        {
          "name": "task_ref",
          "type": "text",
          "required": false
        },
        {
          "name": "text",
          "type": "text",
          "required": true
        }
      ],
      "options": []
    },
    "comments": {
      "description": "List comments on a task.\n\n    Examples: td comments 1 | td comments buy milk\n    ",
      "arguments": [
        {
          "name": "task_ref",
          "type": "text",
          "required": false
        }
      ],
      "options": []
    },
    "completions": {
      "description": "Generate shell completion script.\n\n    Add the output of this command to your shell profile.\n    ",
      "arguments": [
        {
          "name": "shell",
          "type": "choice(bash,zsh,fish)",
          "required": true
        }
      ],
      "options": []
    },
    "delete": {
      "description": "Delete a task. Accepts row number, content match, or task ID.\n\n    Examples: td delete 1 -y | td delete buy milk -y\n    ",
      "arguments": [
        {
          "name": "task_ref",
          "type": "text",
          "required": false
        }
      ],
      "options": [
        {
          "name": "yes",
          "type": "boolean",
          "required": false,
          "flags": [
            "-y",
            "--yes"
          ],
          "help": "Skip confirmation.",
          "is_flag": true,
          "default": false
        }
      ]
    },
    "done": {
      "description": "Complete a task. Accepts row number, content match, or task ID.\n\n    Examples: td done 1 | td done buy milk | td done 8bx9a0c2\n    ",
      "arguments": [
        {
          "name": "task_ref",
          "type": "text",
          "required": false
        }
      ],
      "options": [
        {
          "name": "yes",
          "type": "boolean",
          "required": false,
          "flags": [
            "-y",
            "--yes"
          ],
          "help": "Skip confirmation on fuzzy match.",
          "is_flag": true,
          "default": false
        }
      ]
    },
    "edit": {
      "description": "Update a task. Accepts row number, content match, or task ID.\n\n    Examples: td edit 1 --due friday | td edit buy milk --priority 1\n    ",
      "arguments": [
        {
          "name": "task_ref",
          "type": "text",
          "required": false
        }
      ],
      "options": [
        {
          "name": "content",
          "type": "text",
          "required": false,
          "flags": [
            "--content"
          ],
          "help": "New content.",
          "is_flag": false
        },
        {
          "name": "priority",
          "type": "int(1-4)",
          "required": false,
          "flags": [
            "--priority"
          ],
          "help": "Priority: 1=urgent, 2=high, 3=medium, 4=low.",
          "is_flag": false
        },
        {
          "name": "due",
          "type": "text",
          "required": false,
          "flags": [
            "-d",
            "--due"
          ],
          "help": "New due date.",
          "is_flag": false
        },
        {
          "name": "labels",
          "type": "text",
          "required": false,
          "flags": [
            "-l",
            "--label"
          ],
          "help": "Labels (repeatable).",
          "is_flag": false
        },
        {
          "name": "description",
          "type": "text",
          "required": false,
          "flags": [
            "--desc"
          ],
          "help": "New description.",
          "is_flag": false
        }
      ]
    },
    "focus": {
      "description": "Focus on a single project \u2014 deep work mode.",
      "arguments": [
        {
          "name": "project_name",
          "type": "text",
          "required": true
        }
      ],
      "options": [
        {
          "name": "sort_by",
          "type": "choice(priority,due,project,created)",
          "required": false,
          "flags": [
            "-s",
            "--sort"
          ],
          "help": "Sort order (default: priority).",
          "is_flag": false
        },
        {
          "name": "reverse_sort",
          "type": "boolean",
          "required": false,
          "flags": [
            "--reverse"
          ],
          "help": "Reverse sort order.",
          "is_flag": true,
          "default": false
        }
      ]
    },
    "inbox": {
      "description": "Show unprocessed inbox tasks.",
      "arguments": [],
      "options": []
    },
    "init": {
      "description": "Set up authentication and configuration.",
      "arguments": [],
      "options": []
    },
    "label-add": {
      "description": "Create a new label.",
      "arguments": [
        {
          "name": "name",
          "type": "text",
          "required": true
        }
      ],
      "options": []
    },
    "labels": {
      "description": "List all labels.",
      "arguments": [],
      "options": [
        {
          "name": "search",
          "type": "text",
          "required": false,
          "flags": [
            "-s",
            "--search"
          ],
          "help": "Search labels by name.",
          "is_flag": false
        }
      ]
    },
    "log": {
      "description": "Show completed tasks \u2014 your end-of-day review.",
      "arguments": [],
      "options": [
        {
          "name": "week",
          "type": "boolean",
          "required": false,
          "flags": [
            "--week"
          ],
          "help": "Show completed this week (default: today).",
          "is_flag": true,
          "default": false
        }
      ]
    },
    "ls": {
      "description": "List tasks. Defaults to today + overdue unless filtered.",
      "arguments": [],
      "options": [
        {
          "name": "project_name",
          "type": "text",
          "required": false,
          "flags": [
            "-p",
            "--project"
          ],
          "help": "Filter by project.",
          "is_flag": false
        },
        {
          "name": "label",
          "type": "text",
          "required": false,
          "flags": [
            "-l",
            "--label"
          ],
          "help": "Filter by label.",
          "is_flag": false
        },
        {
          "name": "query",
          "type": "text",
          "required": false,
          "flags": [
            "-f",
            "--filter"
          ],
          "help": "Todoist filter query.",
          "is_flag": false
        },
        {
          "name": "show_all",
          "type": "boolean",
          "required": false,
          "flags": [
            "--all"
          ],
          "help": "Show all tasks (default: today + overdue).",
          "is_flag": true,
          "default": false
        },
        {
          "name": "ids",
          "type": "boolean",
          "required": false,
          "flags": [
            "--ids"
          ],
          "help": "Output only task IDs, one per line.",
          "is_flag": true,
          "default": false
        },
        {
          "name": "sort_by",
          "type": "choice(priority,due,project,created)",
          "required": false,
          "flags": [
            "-s",
            "--sort"
          ],
          "help": "Sort order (default: priority).",
          "is_flag": false
        },
        {
          "name": "reverse_sort",
          "type": "boolean",
          "required": false,
          "flags": [
            "--reverse"
          ],
          "help": "Reverse sort order.",
          "is_flag": true,
          "default": false
        }
      ]
    },
    "move": {
      "description": "Move a task to a different project.\n\n    Examples: td move 1 -p Personal | td move buy milk -p Work\n    ",
      "arguments": [
        {
          "name": "task_ref",
          "type": "text",
          "required": false
        }
      ],
      "options": [
        {
          "name": "project_name",
          "type": "text",
          "required": true,
          "flags": [
            "-p",
            "--project"
          ],
          "help": "Target project.",
          "is_flag": false
        }
      ]
    },
    "next": {
      "description": "Show your highest priority task \u2014 what to work on now.",
      "arguments": [],
      "options": [
        {
          "name": "project_name",
          "type": "text",
          "required": false,
          "flags": [
            "-p",
            "--project"
          ],
          "help": "Scope to a project.",
          "is_flag": false
        }
      ]
    },
    "project-add": {
      "description": "Create a new project.",
      "arguments": [
        {
          "name": "name",
          "type": "text",
          "required": true
        }
      ],
      "options": [
        {
          "name": "parent_name",
          "type": "text",
          "required": false,
          "flags": [
            "--parent"
          ],
          "help": "Parent project name or ID (for sub-projects).",
          "is_flag": false
        },
        {
          "name": "favorite",
          "type": "boolean",
          "required": false,
          "flags": [
            "--favorite"
          ],
          "help": "Mark as favorite.",
          "is_flag": true,
          "default": false
        }
      ]
    },
    "projects": {
      "description": "List all projects.",
      "arguments": [],
      "options": [
        {
          "name": "search",
          "type": "text",
          "required": false,
          "flags": [
            "-s",
            "--search"
          ],
          "help": "Search projects by name.",
          "is_flag": false
        }
      ]
    },
    "quick": {
      "description": "Natural language task creation. Reads from stdin if no args.\n\n    Example: td quick \"Buy milk tomorrow p1 #Errands\"\n    ",
      "arguments": [
        {
          "name": "text",
          "type": "text",
          "required": false
        }
      ],
      "options": []
    },
    "rate-limit": {
      "description": "Show current API rate limit status from cached response headers.",
      "arguments": [],
      "options": []
    },
    "review": {
      "description": "Interactive inbox review \u2014 process tasks one by one.\n\n    Defaults to inbox tasks. Use -p for a project or -f for a filter.\n    ",
      "arguments": [],
      "options": [
        {
          "name": "project_name",
          "type": "text",
          "required": false,
          "flags": [
            "-p",
            "--project"
          ],
          "help": "Review a specific project.",
          "is_flag": false
        },
        {
          "name": "query",
          "type": "text",
          "required": false,
          "flags": [
            "-f",
            "--filter"
          ],
          "help": "Review tasks matching a filter.",
          "is_flag": false
        }
      ]
    },
    "schema": {
      "description": "Output full capability manifest as JSON.",
      "arguments": [],
      "options": []
    },
    "search": {
      "description": "Search tasks by keyword across all projects.\n\n    Example: td search deploy | td search \"blog post\" -p Work\n    ",
      "arguments": [
        {
          "name": "query",
          "type": "text",
          "required": true
        }
      ],
      "options": [
        {
          "name": "project_name",
          "type": "text",
          "required": false,
          "flags": [
            "-p",
            "--project"
          ],
          "help": "Scope to a project.",
          "is_flag": false
        }
      ]
    },
    "section-add": {
      "description": "Create a new section in a project.",
      "arguments": [
        {
          "name": "name",
          "type": "text",
          "required": true
        }
      ],
      "options": [
        {
          "name": "project_name",
          "type": "text",
          "required": true,
          "flags": [
            "-p",
            "--project"
          ],
          "help": "Project name or ID.",
          "is_flag": false
        }
      ]
    },
    "sections": {
      "description": "List sections in a project.",
      "arguments": [],
      "options": [
        {
          "name": "project_name",
          "type": "text",
          "required": true,
          "flags": [
            "-p",
            "--project"
          ],
          "help": "Project name or ID.",
          "is_flag": false
        }
      ]
    },
    "show": {
      "description": "View full task details. Accepts row number, content match, or task ID.\n\n    Examples: td show 1 | td show buy milk | td show 8bx9a0c2\n    ",
      "arguments": [
        {
          "name": "task_ref",
          "type": "text",
          "required": false
        }
      ],
      "options": []
    },
    "today": {
      "description": "Show tasks due today and overdue \u2014 your morning dashboard.",
      "arguments": [],
      "options": [
        {
          "name": "sort_by",
          "type": "choice(priority,due,project,created)",
          "required": false,
          "flags": [
            "-s",
            "--sort"
          ],
          "help": "Sort order (default: priority).",
          "is_flag": false
        },
        {
          "name": "reverse_sort",
          "type": "boolean",
          "required": false,
          "flags": [
            "--reverse"
          ],
          "help": "Reverse sort order.",
          "is_flag": true,
          "default": false
        }
      ]
    },
    "undo": {
      "description": "Reopen a completed task. Accepts row number, content match, or task ID.\n\n    Examples: td undo 1 | td undo buy milk | td undo 8bx9a0c2\n    ",
      "arguments": [
        {
          "name": "task_ref",
          "type": "text",
          "required": false
        }
      ],
      "options": []
    }
  }
}
```


## Configuration Commands

### `td completions zsh`

Generate shell completion script.

```
$ td completions zsh
eval "$(_TD_COMPLETE=zsh_source td)"
```

### `td completions bash`

```
$ td completions bash
eval "$(_TD_COMPLETE=bash_source td)"
```

### `td init`

Interactive authentication setup (prompts for token).

```
$ td init
Get your API token from: https://app.todoist.com/app/settings/integrations/developer

API token: ********
Validating token...
Authenticated. Found 4 project(s).

Config saved to ~/.config/td/config.toml
Try `td ls` to see your tasks.
```


## Command Help

### `td add --help`

```
$ td add --help
Usage: td add [OPTIONS] [CONTENT]...

  Create a new task. Reads from stdin if no content argument.

Options:
  -p, --project TEXT        Project name or ID.
  --priority INTEGER RANGE  Priority: 1=urgent, 2=high, 3=medium, 4=low.
                            [1<=x<=4]
  -d, --due TEXT            Due date (e.g., 'tomorrow', '2026-04-01').
  -l, --label TEXT          Label (repeatable).
  --desc TEXT               Task description.
  -s, --section TEXT        Section name (requires --project).
  --idempotent              Skip if identical task already exists.
  -h, --help                Show this message and exit.
{
  "ok": false,
  "error": {
    "code": "API_ERROR",
    "message": "Unexpected error: 0",
    "suggestion": "",
    "details": {}
  }
}
```

### `td capture --help`

```
$ td capture --help
Usage: td capture [OPTIONS] TEXT...

  Quick-capture to inbox — no parsing, no flags, minimal output.

  Example: td capture call dentist about appointment

Options:
  -h, --help  Show this message and exit.
{
  "ok": false,
  "error": {
    "code": "API_ERROR",
    "message": "Unexpected error: 0",
    "suggestion": "",
    "details": {}
  }
}
```

### `td ls --help`

```
$ td ls --help
Usage: td ls [OPTIONS]

  List tasks. Defaults to today + overdue unless filtered.

Options:
  -p, --project TEXT              Filter by project.
  -l, --label TEXT                Filter by label.
  -f, --filter TEXT               Todoist filter query.
  --all                           Show all tasks (default: today + overdue).
  --ids                           Output only task IDs, one per line.
  -s, --sort [priority|due|project|created]
                                  Sort order (default: priority).
  --reverse                       Reverse sort order.
  -h, --help                      Show this message and exit.
{
  "ok": false,
  "error": {
    "code": "API_ERROR",
    "message": "Unexpected error: 0",
    "suggestion": "",
    "details": {}
  }
}
```

### `td inbox --help`

```
$ td inbox --help
Usage: td inbox [OPTIONS]

  Show unprocessed inbox tasks.

Options:
  -h, --help  Show this message and exit.
{
  "ok": false,
  "error": {
    "code": "API_ERROR",
    "message": "Unexpected error: 0",
    "suggestion": "",
    "details": {}
  }
}
```

### `td today --help`

```
$ td today --help
Usage: td today [OPTIONS]

  Show tasks due today and overdue — your morning dashboard.

Options:
  -s, --sort [priority|due|project|created]
                                  Sort order (default: priority).
  --reverse                       Reverse sort order.
  -h, --help                      Show this message and exit.
{
  "ok": false,
  "error": {
    "code": "API_ERROR",
    "message": "Unexpected error: 0",
    "suggestion": "",
    "details": {}
  }
}
```

### `td next --help`

```
$ td next --help
Usage: td next [OPTIONS]

  Show your highest priority task — what to work on now.

Options:
  -p, --project TEXT  Scope to a project.
  -h, --help          Show this message and exit.
{
  "ok": false,
  "error": {
    "code": "API_ERROR",
    "message": "Unexpected error: 0",
    "suggestion": "",
    "details": {}
  }
}
```

### `td log --help`

```
$ td log --help
Usage: td log [OPTIONS]

  Show completed tasks — your end-of-day review.

Options:
  --week      Show completed this week (default: today).
  -h, --help  Show this message and exit.
{
  "ok": false,
  "error": {
    "code": "API_ERROR",
    "message": "Unexpected error: 0",
    "suggestion": "",
    "details": {}
  }
}
```

### `td focus --help`

```
$ td focus --help
Usage: td focus [OPTIONS] PROJECT_NAME

  Focus on a single project — deep work mode.

Options:
  -s, --sort [priority|due|project|created]
                                  Sort order (default: priority).
  --reverse                       Reverse sort order.
  -h, --help                      Show this message and exit.
{
  "ok": false,
  "error": {
    "code": "API_ERROR",
    "message": "Unexpected error: 0",
    "suggestion": "",
    "details": {}
  }
}
```

### `td show --help`

```
$ td show --help
Usage: td show [OPTIONS] [TASK_REF]...

  View full task details. Accepts row number, content match, or task ID.

  Examples: td show 1 | td show buy milk | td show 8bx9a0c2

Options:
  -h, --help  Show this message and exit.
{
  "ok": false,
  "error": {
    "code": "API_ERROR",
    "message": "Unexpected error: 0",
    "suggestion": "",
    "details": {}
  }
}
```

### `td search --help`

```
$ td search --help
Usage: td search [OPTIONS] QUERY...

  Search tasks by keyword across all projects.

  Example: td search deploy | td search "blog post" -p Work

Options:
  -p, --project TEXT  Scope to a project.
  -h, --help          Show this message and exit.
{
  "ok": false,
  "error": {
    "code": "API_ERROR",
    "message": "Unexpected error: 0",
    "suggestion": "",
    "details": {}
  }
}
```

### `td done --help`

```
$ td done --help
Usage: td done [OPTIONS] [TASK_REF]...

  Complete a task. Accepts row number, content match, or task ID.

  Examples: td done 1 | td done buy milk | td done 8bx9a0c2

Options:
  -y, --yes   Skip confirmation on fuzzy match.
  -h, --help  Show this message and exit.
{
  "ok": false,
  "error": {
    "code": "API_ERROR",
    "message": "Unexpected error: 0",
    "suggestion": "",
    "details": {}
  }
}
```

### `td undo --help`

```
$ td undo --help
Usage: td undo [OPTIONS] [TASK_REF]...

  Reopen a completed task. Accepts row number, content match, or task ID.

  Examples: td undo 1 | td undo buy milk | td undo 8bx9a0c2

Options:
  -h, --help  Show this message and exit.
{
  "ok": false,
  "error": {
    "code": "API_ERROR",
    "message": "Unexpected error: 0",
    "suggestion": "",
    "details": {}
  }
}
```

### `td edit --help`

```
$ td edit --help
Usage: td edit [OPTIONS] [TASK_REF]...

  Update a task. Accepts row number, content match, or task ID.

  Examples: td edit 1 --due friday | td edit buy milk --priority 1

Options:
  --content TEXT            New content.
  --priority INTEGER RANGE  Priority: 1=urgent, 2=high, 3=medium, 4=low.
                            [1<=x<=4]
  -d, --due TEXT            New due date.
  -l, --label TEXT          Labels (repeatable).
  --desc TEXT               New description.
  -h, --help                Show this message and exit.
{
  "ok": false,
  "error": {
    "code": "API_ERROR",
    "message": "Unexpected error: 0",
    "suggestion": "",
    "details": {}
  }
}
```

### `td move --help`

```
$ td move --help
Usage: td move [OPTIONS] [TASK_REF]...

  Move a task to a different project.

  Examples: td move 1 -p Personal | td move buy milk -p Work

Options:
  -p, --project TEXT  Target project.  [required]
  -h, --help          Show this message and exit.
{
  "ok": false,
  "error": {
    "code": "API_ERROR",
    "message": "Unexpected error: 0",
    "suggestion": "",
    "details": {}
  }
}
```

### `td delete --help`

```
$ td delete --help
Usage: td delete [OPTIONS] [TASK_REF]...

  Delete a task. Accepts row number, content match, or task ID.

  Examples: td delete 1 -y | td delete buy milk -y

Options:
  -y, --yes   Skip confirmation.
  -h, --help  Show this message and exit.
{
  "ok": false,
  "error": {
    "code": "API_ERROR",
    "message": "Unexpected error: 0",
    "suggestion": "",
    "details": {}
  }
}
```

### `td quick --help`

```
$ td quick --help
Usage: td quick [OPTIONS] [TEXT]...

  Natural language task creation. Reads from stdin if no args.

  Example: td quick "Buy milk tomorrow p1 #Errands"

Options:
  -h, --help  Show this message and exit.
{
  "ok": false,
  "error": {
    "code": "API_ERROR",
    "message": "Unexpected error: 0",
    "suggestion": "",
    "details": {}
  }
}
```

### `td comment --help`

```
$ td comment --help
Usage: td comment [OPTIONS] [TASK_REF] TEXT...

  Add a comment to a task.

  Examples: td comment 1 "Picked up 2%, not whole"

Options:
  -h, --help  Show this message and exit.
{
  "ok": false,
  "error": {
    "code": "API_ERROR",
    "message": "Unexpected error: 0",
    "suggestion": "",
    "details": {}
  }
}
```

### `td comments --help`

```
$ td comments --help
Usage: td comments [OPTIONS] [TASK_REF]

  List comments on a task.

  Examples: td comments 1 | td comments buy milk

Options:
  -h, --help  Show this message and exit.
{
  "ok": false,
  "error": {
    "code": "API_ERROR",
    "message": "Unexpected error: 0",
    "suggestion": "",
    "details": {}
  }
}
```

### `td projects --help`

```
$ td projects --help
Usage: td projects [OPTIONS]

  List all projects.

Options:
  -s, --search TEXT  Search projects by name.
  -h, --help         Show this message and exit.
{
  "ok": false,
  "error": {
    "code": "API_ERROR",
    "message": "Unexpected error: 0",
    "suggestion": "",
    "details": {}
  }
}
```

### `td project-add --help`

```
$ td project-add --help
Usage: td project-add [OPTIONS] NAME...

  Create a new project.

Options:
  --parent TEXT  Parent project name or ID (for sub-projects).
  --favorite     Mark as favorite.
  -h, --help     Show this message and exit.
{
  "ok": false,
  "error": {
    "code": "API_ERROR",
    "message": "Unexpected error: 0",
    "suggestion": "",
    "details": {}
  }
}
```

### `td sections --help`

```
$ td sections --help
Usage: td sections [OPTIONS]

  List sections in a project.

Options:
  -p, --project TEXT  Project name or ID.  [required]
  -h, --help          Show this message and exit.
{
  "ok": false,
  "error": {
    "code": "API_ERROR",
    "message": "Unexpected error: 0",
    "suggestion": "",
    "details": {}
  }
}
```

### `td section-add --help`

```
$ td section-add --help
Usage: td section-add [OPTIONS] NAME...

  Create a new section in a project.

Options:
  -p, --project TEXT  Project name or ID.  [required]
  -h, --help          Show this message and exit.
{
  "ok": false,
  "error": {
    "code": "API_ERROR",
    "message": "Unexpected error: 0",
    "suggestion": "",
    "details": {}
  }
}
```

### `td labels --help`

```
$ td labels --help
Usage: td labels [OPTIONS]

  List all labels.

Options:
  -s, --search TEXT  Search labels by name.
  -h, --help         Show this message and exit.
{
  "ok": false,
  "error": {
    "code": "API_ERROR",
    "message": "Unexpected error: 0",
    "suggestion": "",
    "details": {}
  }
}
```

### `td label-add --help`

```
$ td label-add --help
Usage: td label-add [OPTIONS] NAME...

  Create a new label.

Options:
  -h, --help  Show this message and exit.
{
  "ok": false,
  "error": {
    "code": "API_ERROR",
    "message": "Unexpected error: 0",
    "suggestion": "",
    "details": {}
  }
}
```

### `td review --help`

```
$ td review --help
Usage: td review [OPTIONS]

  Interactive inbox review — process tasks one by one.

  Defaults to inbox tasks. Use -p for a project or -f for a filter.

Options:
  -p, --project TEXT  Review a specific project.
  -f, --filter TEXT   Review tasks matching a filter.
  -h, --help          Show this message and exit.
{
  "ok": false,
  "error": {
    "code": "API_ERROR",
    "message": "Unexpected error: 0",
    "suggestion": "",
    "details": {}
  }
}
```

### `td rate-limit --help`

```
$ td rate-limit --help
Usage: td rate-limit [OPTIONS]

  Show current API rate limit status from cached response headers.

Options:
  -h, --help  Show this message and exit.
{
  "ok": false,
  "error": {
    "code": "API_ERROR",
    "message": "Unexpected error: 0",
    "suggestion": "",
    "details": {}
  }
}
```

### `td schema --help`

```
$ td schema --help
Usage: td schema [OPTIONS]

  Output full capability manifest as JSON.

Options:
  -h, --help  Show this message and exit.
{
  "ok": false,
  "error": {
    "code": "API_ERROR",
    "message": "Unexpected error: 0",
    "suggestion": "",
    "details": {}
  }
}
```

