#!/usr/bin/env python3
"""Generate example command output for documentation.

Runs every td command with mocked API data and captures output
in Rich, JSON, and Plain modes. Writes results to docs/examples.md.
"""

from __future__ import annotations

import json
from unittest.mock import MagicMock, patch

from click.testing import CliRunner

from td.cli import cli

# ---------------------------------------------------------------------------
# Mock data factories
# ---------------------------------------------------------------------------


def _make_task(
    id: str = "8bx9a0c2",
    content: str = "Review PR for auth module",
    priority: int = 4,
    labels: list[str] | None = None,
    due_string: str | None = "Mar 25",
    due_date: str | None = "2026-03-25",
    project_id: str = "220474322",
    description: str = "",
) -> MagicMock:
    task = MagicMock()
    task.id = id
    task.content = content
    task.priority = priority
    task.labels = labels or []
    task.project_id = project_id
    task.description = description
    if due_string:
        task.due = MagicMock()
        task.due.string = due_string
        task.due.date = due_date
    else:
        task.due = None
    task.to_dict.return_value = {
        "id": id,
        "content": content,
        "priority": priority,
        "labels": labels or [],
        "project_id": project_id,
        "description": description,
        "due": {"string": due_string, "date": due_date} if due_string else None,
    }
    return task


def _make_project(
    id: str = "220474322",
    name: str = "Work",
    is_favorite: bool = False,
    is_inbox_project: bool = False,
) -> MagicMock:
    proj = MagicMock()
    proj.id = id
    proj.name = name
    proj.is_favorite = is_favorite
    proj.is_inbox_project = is_inbox_project
    proj.to_dict.return_value = {
        "id": id,
        "name": name,
        "is_favorite": is_favorite,
    }
    return proj


def _make_section(id: str = "s1", name: str = "In Progress") -> MagicMock:
    sec = MagicMock()
    sec.id = id
    sec.name = name
    sec.to_dict.return_value = {"id": id, "name": name}
    return sec


def _make_label(id: str = "lbl1", name: str = "urgent") -> MagicMock:
    lbl = MagicMock()
    lbl.id = id
    lbl.name = name
    lbl.to_dict.return_value = {"id": id, "name": name}
    return lbl


# ---------------------------------------------------------------------------
# Sample data sets
# ---------------------------------------------------------------------------

TASKS = [
    _make_task(
        id="8bx9a0c2",
        content="Review PR for auth module",
        priority=4,
        labels=["work", "code-review"],
        due_string="Mar 25",
        due_date="2026-03-25",
    ),
    _make_task(
        id="7ky3m1f9",
        content="Buy groceries",
        priority=1,
        labels=["errands"],
        due_string="Mar 26",
        due_date="2026-03-26",
    ),
    _make_task(
        id="4np6r2d5",
        content="Write blog post draft",
        priority=3,
        labels=["writing"],
        due_string="Mar 28",
        due_date="2026-03-28",
    ),
    _make_task(
        id="1aq8s4g7",
        content="Schedule dentist appointment",
        priority=2,
        due_string=None,
    ),
]

PROJECTS = [
    _make_project("220474322", "Inbox", is_inbox_project=True),
    _make_project("220474323", "Work", is_favorite=True),
    _make_project("220474324", "Personal"),
    _make_project("220474325", "Side Projects"),
]

SECTIONS = [
    _make_section("s1", "Backlog"),
    _make_section("s2", "In Progress"),
    _make_section("s3", "Done"),
]

LABELS = [
    _make_label("lbl1", "urgent"),
    _make_label("lbl2", "work"),
    _make_label("lbl3", "errands"),
    _make_label("lbl4", "writing"),
    _make_label("lbl5", "code-review"),
]


# ---------------------------------------------------------------------------
# Runner helpers
# ---------------------------------------------------------------------------


def run_cmd(args: list[str], api: MagicMock | None = None) -> str:
    """Run a CLI command and return the output."""
    runner = CliRunner()
    invoke_kwargs = {"args": args, "prog_name": "td"}
    if api:
        with (
            patch("td.cli.tasks.get_client", return_value=api),
            patch("td.cli.projects.get_client", return_value=api),
            patch("td.cli.sections.get_client", return_value=api),
            patch("td.cli.labels.get_client", return_value=api),
            patch("td.cli.comments.get_client", return_value=api),
        ):
            result = runner.invoke(cli, **invoke_kwargs)
    else:
        result = runner.invoke(cli, **invoke_kwargs)
    return result.output


def make_api() -> MagicMock:
    """Create a fully configured mock API."""
    api = MagicMock()
    api.get_tasks.return_value = iter([TASKS])
    api.filter_tasks.return_value = iter([TASKS[:2]])
    api.get_projects.return_value = iter([PROJECTS])
    api.search_projects.return_value = iter([[PROJECTS[1]]])
    api.get_sections.return_value = iter([SECTIONS])
    api.get_labels.return_value = iter([LABELS])
    api.search_labels.return_value = iter([[LABELS[0]]])
    api.add_task.return_value = TASKS[0]
    api.add_task_quick.return_value = TASKS[1]
    api.update_task.return_value = TASKS[0]
    api.get_task.return_value = TASKS[0]
    api.complete_task.return_value = None
    api.uncomplete_task.return_value = None
    api.delete_task.return_value = None
    api.move_task.return_value = True
    api.add_project.return_value = PROJECTS[1]
    api.add_section.return_value = SECTIONS[1]
    api.add_label.return_value = LABELS[0]
    comment_mock = MagicMock()
    comment_mock.id = "c1"
    comment_mock.content = "Picked up 2%, not whole"
    comment_mock.posted_at = "2026-03-25T10:30:00Z"
    comment_mock.to_dict.return_value = {
        "id": "c1",
        "content": "Picked up 2%, not whole",
        "posted_at": "2026-03-25T10:30:00Z",
    }
    api.add_comment.return_value = comment_mock
    api.get_comments.return_value = iter([[comment_mock]])
    return api


# ---------------------------------------------------------------------------
# Generate examples
# ---------------------------------------------------------------------------


def generate() -> str:
    lines: list[str] = []

    def heading(text: str, level: int = 2) -> None:
        lines.append(f"\n{'#' * level} {text}\n")

    def example(title: str, cmd: str, output: str) -> None:
        lines.append(f"### `{cmd}`\n")
        if title:
            lines.append(f"{title}\n")
        lines.append("```")
        lines.append(f"$ {cmd}")
        lines.append(output.rstrip())
        lines.append("```\n")

    lines.append("# td — Command Examples\n")
    lines.append("Auto-generated example output for every td command.\n")

    # --- td --help ---
    heading("Global Help")
    output = run_cmd(["--help"])
    example("", "td --help", output)

    # --- td --version ---
    heading("Version")
    output = run_cmd(["--version"])
    example("", "td --version", output)

    # --- td ls ---
    heading("Task Commands")

    output = run_cmd(["--json", "ls"], make_api())
    example("List all tasks (JSON mode).", "td --json ls", output)

    output = run_cmd(["--plain", "ls"], make_api())
    example("List all tasks (plain mode).", "td --plain ls", output)

    # --- td ls --filter ---
    output = run_cmd(["--json", "ls", "-f", "today & #Work"], make_api())
    example("List tasks with a Todoist filter query.", 'td --json ls -f "today & #Work"', output)

    # --- td inbox ---
    output = run_cmd(["--json", "inbox"], make_api())
    example("Show inbox tasks.", "td --json inbox", output)

    # --- td add ---
    add_args = [
        "--json",
        "add",
        "Review PR for auth module",
        "-p",
        "Work",
        "--priority",
        "1",
        "-d",
        "tomorrow",
        "-l",
        "work",
        "-l",
        "code-review",
    ]
    output = run_cmd(add_args, make_api())
    add_cmd = (
        "td --json add "
        '"Review PR for auth module" '
        "-p Work --priority 1 -d tomorrow -l work -l code-review"
    )
    example(
        "Create a task with project, priority, due date, and labels.",
        add_cmd,
        output,
    )

    # --- td add --idempotent ---
    output = run_cmd(
        ["--json", "add", "Review PR for auth module", "--idempotent"],
        make_api(),
    )
    example(
        "Idempotent add — returns existing task if content matches.",
        'td --json add "Review PR for auth module" --idempotent',
        output,
    )

    # --- td quick ---
    output = run_cmd(
        ["--json", "quick", "Buy groceries tomorrow p2 #errands"],
        make_api(),
    )
    example(
        "Natural language task creation.",
        'td --json quick "Buy groceries tomorrow p2 #errands"',
        output,
    )

    # --- td capture ---
    output = run_cmd(["--json", "capture", "Call dentist about appointment"], make_api())
    example(
        "Quick-capture to inbox — no parsing, no flags.",
        "td --json capture Call dentist about appointment",
        output,
    )

    # --- td done ---
    output = run_cmd(["--json", "done", "8bx9a0c2"], make_api())
    example("Complete a task.", "td --json done 8bx9a0c2", output)

    # --- td undo ---
    output = run_cmd(["--json", "undo", "8bx9a0c2"], make_api())
    example("Reopen a completed task.", "td --json undo 8bx9a0c2", output)

    # --- td edit ---
    edit_args = [
        "--json",
        "edit",
        "8bx9a0c2",
        "--content",
        "Review PR for auth module (updated)",
        "--priority",
        "2",
    ]
    output = run_cmd(edit_args, make_api())
    edit_cmd = (
        'td --json edit 8bx9a0c2 --content "Review PR for auth module (updated)" --priority 2'
    )
    example("Update a task.", edit_cmd, output)

    # --- td show ---
    output = run_cmd(["--json", "show", "8bx9a0c2"], make_api())
    example("View full task details.", "td --json show 8bx9a0c2", output)

    # --- td move ---
    output = run_cmd(["--json", "move", "8bx9a0c2", "-p", "Work"], make_api())
    example("Move a task to a different project.", 'td --json move 8bx9a0c2 -p "Work"', output)

    # --- td search ---
    output = run_cmd(["--json", "search", "review"], make_api())
    example("Search tasks by keyword.", "td --json search review", output)

    # --- td delete ---
    output = run_cmd(["--json", "delete", "8bx9a0c2", "--yes"], make_api())
    example(
        "Delete a task (with --yes to skip confirmation).",
        "td --json delete 8bx9a0c2 --yes",
        output,
    )

    # --- td comment ---
    output = run_cmd(["--json", "comment", "8bx9a0c2", "Picked up 2%, not whole"], make_api())
    example(
        "Add a comment to a task.",
        'td --json comment 8bx9a0c2 "Picked up 2%, not whole"',
        output,
    )

    # --- td comments ---
    output = run_cmd(["--json", "comments", "8bx9a0c2"], make_api())
    example("List comments on a task.", "td --json comments 8bx9a0c2", output)

    # --- Workflow Commands ---
    heading("Workflow Commands")

    # --- td today ---
    output = run_cmd(["--json", "today"], make_api())
    example(
        "Show tasks due today and overdue — your morning dashboard.",
        "td --json today",
        output,
    )

    # --- td next ---
    output = run_cmd(["--json", "next"], make_api())
    example("Show your highest priority task.", "td --json next", output)

    # --- td focus ---
    output = run_cmd(["--json", "focus", "Work"], make_api())
    example("Focus on a single project.", 'td --json focus "Work"', output)

    # --- td projects ---
    heading("Organization Commands")

    output = run_cmd(["--json", "projects"], make_api())
    example("List all projects.", "td --json projects", output)

    output = run_cmd(["--plain", "projects"], make_api())
    example("List projects (plain mode).", "td --plain projects", output)

    # --- td projects --search ---
    output = run_cmd(["--json", "projects", "-s", "Work"], make_api())
    example("Search projects.", 'td --json projects -s "Work"', output)

    # --- td project-add ---
    output = run_cmd(["--json", "project-add", "Side Projects"], make_api())
    example("Create a new project.", 'td --json project-add "Side Projects"', output)

    # --- td sections ---
    output = run_cmd(["--json", "sections", "-p", "Work"], make_api())
    example("List sections in a project.", 'td --json sections -p "Work"', output)

    # --- td section-add ---
    output = run_cmd(["--json", "section-add", "In Progress", "-p", "Work"], make_api())
    example(
        "Create a new section in a project.",
        'td --json section-add "In Progress" -p "Work"',
        output,
    )

    # --- td labels ---
    output = run_cmd(["--json", "labels"], make_api())
    example("List all labels.", "td --json labels", output)

    output = run_cmd(["--plain", "labels"], make_api())
    example("List labels (plain mode).", "td --plain labels", output)

    # --- td label-add ---
    output = run_cmd(["--json", "label-add", "urgent"], make_api())
    example("Create a new label.", "td --json label-add urgent", output)

    # --- td schema ---
    heading("AI-Native Commands")

    output = run_cmd(["schema"])
    # Pretty-print just a snippet
    schema = json.loads(output)
    example(
        "Output the full capability manifest. Agents call this once to learn everything.",
        "td schema",
        json.dumps(schema, indent=2),
    )

    # --- td completions ---
    heading("Configuration Commands")

    output = run_cmd(["completions", "zsh"])
    example("Generate shell completion script.", "td completions zsh", output)

    output = run_cmd(["completions", "bash"])
    example("", "td completions bash", output)

    # --- td init ---
    example(
        "Interactive authentication setup (prompts for token).",
        "td init",
        "Get your API token from: "
        "https://app.todoist.com/app/settings/integrations/developer"
        "\n\nAPI token: ********"
        "\nValidating token..."
        "\nAuthenticated. Found 4 project(s)."
        "\n\nConfig saved to ~/.config/td/config.toml"
        "\nTry `td ls` to see your tasks.",
    )

    # --- Individual command help ---
    heading("Command Help")

    cmds = [
        "add",
        "capture",
        "ls",
        "inbox",
        "today",
        "next",
        "log",
        "focus",
        "show",
        "search",
        "done",
        "undo",
        "edit",
        "move",
        "delete",
        "quick",
        "comment",
        "comments",
        "projects",
        "project-add",
        "sections",
        "section-add",
        "labels",
        "label-add",
        "rate-limit",
        "schema",
    ]
    for cmd in cmds:
        output = run_cmd([cmd, "--help"])
        example("", f"td {cmd} --help", output)

    return "\n".join(lines)


if __name__ == "__main__":
    print(generate())
