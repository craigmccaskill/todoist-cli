"""Tier 3: Architectural tests — structural invariants that should never be violated."""

from __future__ import annotations

import ast
from pathlib import Path


class TestCoreCLIBoundary:
    """core/ must never import from cli/ — it's a standalone library."""

    def test_no_core_imports_from_cli(self) -> None:
        core_dir = Path("src/td/core")
        violations: list[str] = []

        for py_file in sorted(core_dir.glob("*.py")):
            tree = ast.parse(py_file.read_text())
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom) and node.module and node.module.startswith(
                    "td.cli"
                ):
                    violations.append(f"{py_file.name}:{node.lineno} imports {node.module}")

        assert violations == [], f"core/ imports from cli/: {violations}"
