"""td — AI-native Todoist CLI."""

from pathlib import Path

__version__ = (Path(__file__).parent / "VERSION").read_text().strip()
