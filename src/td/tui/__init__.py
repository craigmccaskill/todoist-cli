"""TUI components for interactive task management."""

from __future__ import annotations


def is_available() -> bool:
    """Check if textual is installed."""
    try:
        import textual  # noqa: F401

        return True
    except ImportError:
        return False
