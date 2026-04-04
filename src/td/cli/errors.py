"""Structured error handling with codes and suggestions."""

from __future__ import annotations

import json
from typing import Any

import click
from rich.console import Console

from td.cli.output import OutputMode

# Error codes
AUTH_MISSING = "AUTH_MISSING"
AUTH_INVALID = "AUTH_INVALID"
TASK_NOT_FOUND = "TASK_NOT_FOUND"
PROJECT_NOT_FOUND = "PROJECT_NOT_FOUND"
SECTION_NOT_FOUND = "SECTION_NOT_FOUND"
LABEL_NOT_FOUND = "LABEL_NOT_FOUND"
VALIDATION_ERROR = "VALIDATION_ERROR"
API_ERROR = "API_ERROR"
API_RATE_LIMIT = "API_RATE_LIMIT"
DUPLICATE_TASK = "DUPLICATE_TASK"


class TdError(click.ClickException):
    """Base error with structured output."""

    code: str = API_ERROR
    suggestion: str = ""

    def __init__(
        self,
        message: str,
        *,
        code: str | None = None,
        suggestion: str = "",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        if code is not None:
            self.code = code
        if suggestion:
            self.suggestion = suggestion
        self.details = details or {}

    def format_json(self) -> str:
        """Format as structured JSON for stderr."""
        error_obj: dict[str, Any] = {
            "ok": False,
            "error": {
                "code": self.code,
                "message": self.message,
                "suggestion": self.suggestion,
                "details": self.details,
            },
        }
        return json.dumps(error_obj, indent=2, default=str)

    def format_rich(self) -> None:
        """Print formatted error to stderr using Rich."""
        console = Console(stderr=True)
        console.print(f"[red bold]Error:[/red bold] {self.message}")
        if self.details:
            for key, val in self.details.items():
                console.print(f"  [dim]{key}:[/dim] {val}")
        if self.suggestion:
            console.print(f"  [yellow]Suggestion:[/yellow] {self.suggestion}")

    def format_plain(self) -> str:
        """Format as plain text for stderr."""
        lines = [f"Error: {self.message}"]
        if self.suggestion:
            lines.append(f"Suggestion: {self.suggestion}")
        return "\n".join(lines)


class TdAuthError(TdError):
    """Authentication error."""

    code = AUTH_MISSING
    suggestion = "Run `td init` to set up authentication, or set TD_API_TOKEN."


class TdNotFoundError(TdError):
    """Resource not found."""

    code = TASK_NOT_FOUND


class TdProjectNotFoundError(TdError):
    """Project not found."""

    code = PROJECT_NOT_FOUND
    suggestion = "Run `td projects` to list available projects."


class TdValidationError(TdError):
    """Invalid input."""

    code = VALIDATION_ERROR


class TdApiError(TdError):
    """Todoist API error."""

    code = API_ERROR


class TdRateLimitError(TdError):
    """Rate limit exceeded."""

    code = API_RATE_LIMIT
    suggestion = "Wait a moment and try again. Todoist allows 450 requests per 15 minutes."


def handle_error(error: TdError, mode: OutputMode) -> None:
    """Render a TdError to stderr in the appropriate output mode."""
    if mode == OutputMode.JSON:
        click.echo(error.format_json(), err=True)
    elif mode == OutputMode.RICH:
        error.format_rich()
    else:
        click.echo(error.format_plain(), err=True)


def map_api_exception(exc: Exception) -> TdError:
    """Map SDK/httpx exceptions to structured TdError subclasses."""
    from httpx import HTTPStatusError

    if isinstance(exc, HTTPStatusError):
        status = exc.response.status_code
        if status == 401:
            return TdAuthError(
                "Invalid API token.",
                code=AUTH_INVALID,
                suggestion="Check your token at https://app.todoist.com/app/settings/integrations/developer",
            )
        if status == 403:
            return TdApiError(
                "Access forbidden.",
                suggestion="Check your permissions for this resource.",
            )
        if status == 404:
            return TdNotFoundError("Resource not found.")
        if status == 429:
            return TdRateLimitError("Rate limit exceeded.")
        return TdApiError(
            f"API error: {status} {exc.response.reason_phrase}",
            details={"status_code": status},
        )

    return TdApiError(f"Unexpected error: {exc}")


def map_core_exception(exc: Exception) -> TdError:
    """Map a core-layer exception to a CLI TdError, preserving code/message/suggestion."""
    from td.core.exceptions import AuthError, TdCoreError

    if not isinstance(exc, TdCoreError):
        return TdApiError(f"Unexpected error: {exc}")

    if isinstance(exc, AuthError):
        return TdAuthError(exc.message, suggestion=exc.suggestion)

    # Generic mapping — preserves code, message, suggestion, and details
    return TdError(
        exc.message,
        code=exc.code,
        suggestion=exc.suggestion,
        details=exc.details,
    )
