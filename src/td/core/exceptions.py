"""Core-layer exceptions — no CLI or Click dependency."""

from __future__ import annotations

from typing import Any

# Error codes (shared with CLI layer)
AUTH_MISSING = "AUTH_MISSING"
TASK_NOT_FOUND = "TASK_NOT_FOUND"
PROJECT_NOT_FOUND = "PROJECT_NOT_FOUND"
SECTION_NOT_FOUND = "SECTION_NOT_FOUND"
LABEL_NOT_FOUND = "LABEL_NOT_FOUND"


class TdCoreError(Exception):
    """Base exception for the core layer."""

    code: str = "CORE_ERROR"

    def __init__(
        self,
        message: str,
        *,
        code: str | None = None,
        suggestion: str = "",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        if code is not None:
            self.code = code
        self.suggestion = suggestion
        self.details = details or {}


class AuthError(TdCoreError):
    """No API token available."""

    code = AUTH_MISSING

    def __init__(self) -> None:
        super().__init__(
            "No API token configured.",
            suggestion="Run `td init` or set TD_API_TOKEN.",
        )


class ProjectNotFoundError(TdCoreError):
    """Project not found."""

    code = PROJECT_NOT_FOUND


class SectionNotFoundError(TdCoreError):
    """Section not found."""

    code = SECTION_NOT_FOUND


class LabelNotFoundError(TdCoreError):
    """Label not found."""

    code = LABEL_NOT_FOUND
