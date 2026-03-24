# td — Command Examples

Auto-generated example output for every td command.


## Global Help

### `td --help`

```
$ td --help
Usage: cli [OPTIONS] COMMAND [ARGS]...

  td — AI-native Todoist CLI.

Options:
  --json     Force JSON output.
  --plain    Force plain text output (no color).
  --version  Show the version and exit.
  --help     Show this message and exit.

Commands:
  add          Create a new task.
  completions  Generate shell completion script.
  delete       Delete a task.
  done         Complete a task.
  edit         Update a task.
  inbox        Show unprocessed inbox tasks.
  init         Set up authentication and configuration.
  labels       List all labels.
  ls           List tasks.
  projects     List all projects.
  quick        Natural language task creation.
  schema       Output full capability manifest as JSON.
  sections     List sections in a project.
```


## Version

### `td --version`

```
$ td --version
td, version 0.1.0
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
      }
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
      }
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
    }
  ]
}
```

### `td --plain ls`

List all tasks (plain mode).

```
$ td --plain ls
ID	CONTENT	DUE	PRIORITY	LABELS
8bx9a0c2	Review PR for auth module	2026-03-25	p1	work,code-review
7ky3m1f9	Buy groceries	2026-03-26	p4	errands
4np6r2d5	Write blog post draft	2026-03-28	p2	writing
1aq8s4g7	Schedule dentist appointment		p3
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
      }
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
      }
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
      }
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
      }
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
    "created": true
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
    }
  }
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


## AI-Native Commands

### `td schema`

Output the full capability manifest. Agents call this once to learn everything.

```
$ td schema
{
  "name": "td",
  "version": "0.1.0",
  "description": "AI-native Todoist CLI",
  "commands": {
    "add": {
      "description": "Create a new task.",
      "arguments": [
        {
          "name": "content",
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
          "help": "Priority 1-4 (1=urgent).",
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
      "description": "Delete a task.",
      "arguments": [
        {
          "name": "task_id",
          "type": "text",
          "required": true
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
      "description": "Complete a task.",
      "arguments": [
        {
          "name": "task_id",
          "type": "text",
          "required": true
        }
      ],
      "options": []
    },
    "edit": {
      "description": "Update a task.",
      "arguments": [
        {
          "name": "task_id",
          "type": "text",
          "required": true
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
          "help": "Priority 1-4 (1=urgent).",
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
    "ls": {
      "description": "List tasks.",
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
      "description": "Natural language task creation.\n\n    Example: td quick \"Buy milk tomorrow p1 #Errands\"\n    ",
      "arguments": [
        {
          "name": "text",
          "type": "text",
          "required": true
        }
      ],
      "options": []
    },
    "schema": {
      "description": "Output full capability manifest as JSON.",
      "arguments": [],
      "options": []
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
Usage: cli add [OPTIONS] CONTENT...

  Create a new task.

Options:
  -p, --project TEXT        Project name or ID.
  --priority INTEGER RANGE  Priority 1-4 (1=urgent).  [1<=x<=4]
  -d, --due TEXT            Due date (e.g., 'tomorrow', '2026-04-01').
  -l, --label TEXT          Label (repeatable).
  --desc TEXT               Task description.
  --idempotent              Skip if identical task already exists.
  --help                    Show this message and exit.
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
Usage: cli ls [OPTIONS]

  List tasks.

Options:
  -p, --project TEXT  Filter by project.
  -l, --label TEXT    Filter by label.
  -f, --filter TEXT   Todoist filter query.
  --help              Show this message and exit.
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
Usage: cli done [OPTIONS] TASK_ID

  Complete a task.

Options:
  --help  Show this message and exit.
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
Usage: cli edit [OPTIONS] TASK_ID

  Update a task.

Options:
  --content TEXT            New content.
  --priority INTEGER RANGE  Priority 1-4 (1=urgent).  [1<=x<=4]
  -d, --due TEXT            New due date.
  -l, --label TEXT          Labels (repeatable).
  --desc TEXT               New description.
  --help                    Show this message and exit.
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
Usage: cli delete [OPTIONS] TASK_ID

  Delete a task.

Options:
  -y, --yes  Skip confirmation.
  --help     Show this message and exit.
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
Usage: cli quick [OPTIONS] TEXT...

  Natural language task creation.

  Example: td quick "Buy milk tomorrow p1 #Errands"

Options:
  --help  Show this message and exit.
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
Usage: cli inbox [OPTIONS]

  Show unprocessed inbox tasks.

Options:
  --help  Show this message and exit.
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
Usage: cli projects [OPTIONS]

  List all projects.

Options:
  -s, --search TEXT  Search projects by name.
  --help             Show this message and exit.
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
Usage: cli sections [OPTIONS]

  List sections in a project.

Options:
  -p, --project TEXT  Project name or ID.  [required]
  --help              Show this message and exit.
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
Usage: cli labels [OPTIONS]

  List all labels.

Options:
  -s, --search TEXT  Search labels by name.
  --help             Show this message and exit.
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
Usage: cli schema [OPTIONS]

  Output full capability manifest as JSON.

Options:
  --help  Show this message and exit.
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

