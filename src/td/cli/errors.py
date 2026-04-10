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
API_FORBIDDEN = "API_FORBIDDEN"
API_TIMEOUT = "API_TIMEOUT"
API_SERVER_ERROR = "API_SERVER_ERROR"
NETWORK_ERROR = "NETWORK_ERROR"
CACHE_ERROR = "CACHE_ERROR"
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
    suggestion = "Run `td init` or set TD_API_TOKEN."


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


class TdForbiddenError(TdError):
    """Access forbidden."""

    code = API_FORBIDDEN
    suggestion = "Check your permissions for this resource in Todoist."


class TdTimeoutError(TdError):
    """Request timed out."""

    code = API_TIMEOUT
    suggestion = "Check your internet connection and try again."


class TdServerError(TdError):
    """Todoist server error."""

    code = API_SERVER_ERROR
    suggestion = "Todoist may be experiencing issues. Try again in a few minutes."


class TdNetworkError(TdError):
    """Network connectivity error."""

    code = NETWORK_ERROR
    suggestion = (
        "Check your internet connection. "
        "If the problem persists, check https://status.todoist.com for service status."
    )


class TdCacheError(TdError):
    """Cache read/write error."""

    code = CACHE_ERROR


def handle_error(error: TdError, mode: OutputMode) -> None:
    """Render a TdError to stderr in the appropriate output mode."""
    if mode == OutputMode.JSON:
        click.echo(error.format_json(), err=True)
    elif mode == OutputMode.RICH:
        error.format_rich()
    else:
        click.echo(error.format_plain(), err=True)


def _extract_response_detail(exc: Exception) -> str:
    """Try to extract a human-readable message from an HTTP error response body."""
    from httpx import HTTPStatusError

    if not isinstance(exc, HTTPStatusError):
        return ""
    try:
        text = exc.response.text.strip()
        if not text:
            return ""
        # Todoist API may return JSON with an error message
        import json

        data = json.loads(text)
        if isinstance(data, str):
            return data
        if isinstance(data, dict):
            return str(data.get("error", data.get("message", text)))
        return text  # pragma: no cover
    except (ValueError, AttributeError):
        return text if text else ""


def map_api_exception(exc: Exception) -> TdError:
    """Map SDK/httpx exceptions to structured TdError subclasses."""
    import httpx

    # Network-level errors (no HTTP response received)
    if isinstance(exc, httpx.ConnectTimeout):
        return TdTimeoutError(
            "Connection timed out while reaching Todoist.",
            suggestion="Check your internet connection and try again.",
        )
    if isinstance(exc, httpx.ReadTimeout):
        return TdTimeoutError(
            "Request timed out waiting for Todoist to respond.",
            suggestion="Todoist may be slow. Try again in a moment.",
        )
    if isinstance(exc, httpx.ConnectError):
        return TdNetworkError(
            "Could not connect to Todoist API.",
            suggestion=(
                "Check your internet connection. "
                "If the problem persists, check https://status.todoist.com for service status."
            ),
        )
    if isinstance(exc, httpx.TimeoutException):
        return TdTimeoutError(
            "Request to Todoist timed out.",
            suggestion="Check your internet connection and try again.",
        )

    # HTTP status errors (response received with error code)
    if isinstance(exc, httpx.HTTPStatusError):
        status = exc.response.status_code
        if status == 400:
            detail = _extract_response_detail(exc)
            message = f"Bad request: {detail}" if detail else "Bad request to Todoist API."
            return TdValidationError(
                message,
                suggestion="Check command arguments. Use --help for usage details.",
                details={"status_code": status},
            )
        if status == 401:
            return TdAuthError(
                "Invalid API token.",
                code=AUTH_INVALID,
                suggestion="Check your token at https://app.todoist.com/app/settings/integrations/developer",
            )
        if status == 403:
            return TdForbiddenError(
                "Access forbidden. You don't have permission for this resource.",
                suggestion="Check your permissions for this resource in Todoist.",
            )
        if status == 404:
            detail = _extract_response_detail(exc)
            message = f"Resource not found: {detail}" if detail else "Resource not found."
            return TdNotFoundError(
                message,
                suggestion="Verify the task, project, or label exists. "
                "Use `td ls` or `td projects` to see available items.",
            )
        if status == 408:
            return TdTimeoutError(
                "Request timed out on the server side.",
                suggestion="Try again. If the problem persists, Todoist may be under heavy load.",
                details={"status_code": status},
            )
        if status == 429:
            return TdRateLimitError("Rate limit exceeded.")
        if status == 500:
            detail = _extract_response_detail(exc)
            message = (
                f"Todoist internal server error: {detail}"
                if detail
                else "Todoist internal server error."
            )
            return TdServerError(
                message,
                suggestion="This is a Todoist server issue. Try again in a few minutes.",
                details={"status_code": status},
            )
        if status == 502:
            return TdServerError(
                "Todoist returned a bad gateway error.",
                suggestion="Todoist may be deploying updates. Try again in a minute.",
                details={"status_code": status},
            )
        if status == 503:
            return TdServerError(
                "Todoist is temporarily unavailable.",
                suggestion="Todoist is down for maintenance or overloaded. "
                "Check https://status.todoist.com and try again later.",
                details={"status_code": status},
            )
        if status == 504:
            return TdServerError(
                "Todoist gateway timed out.",
                suggestion="Todoist is responding slowly. Try again in a few minutes.",
                details={"status_code": status},
            )
        # Generic fallback for other HTTP errors
        detail = _extract_response_detail(exc)
        message = f"API error: {detail}" if detail else f"API error (HTTP {status})."
        return TdApiError(
            message,
            suggestion="Try again or check https://status.todoist.com for service status.",
            details={"status_code": status},
        )

    return TdApiError(
        f"Unexpected error: {exc}",
        suggestion="If this persists, run with TD_DEBUG=1 for more details.",
    )


def map_core_exception(exc: Exception) -> TdError:
    """Map a core-layer exception to a CLI TdError, preserving code/message/suggestion."""
    from td.core.exceptions import (
        AuthError,
        LabelNotFoundError,
        ProjectNotFoundError,
        SectionNotFoundError,
        TdCoreError,
    )

    if not isinstance(exc, TdCoreError):
        return TdApiError(
            f"Unexpected error: {exc}",
            suggestion="If this persists, run with TD_DEBUG=1 for more details.",
        )

    if isinstance(exc, AuthError):
        return TdAuthError(exc.message, suggestion=exc.suggestion)

    if isinstance(exc, ProjectNotFoundError):
        return TdProjectNotFoundError(
            exc.message,
            suggestion=exc.suggestion or "Run `td projects` to list available projects.",
            details=exc.details,
        )

    if isinstance(exc, SectionNotFoundError):
        return TdNotFoundError(
            exc.message,
            code=SECTION_NOT_FOUND,
            suggestion=exc.suggestion or "Run `td sections -p <project>` to list sections.",
            details=exc.details,
        )

    if isinstance(exc, LabelNotFoundError):
        return TdNotFoundError(
            exc.message,
            code=LABEL_NOT_FOUND,
            suggestion=exc.suggestion or "Run `td labels` to list available labels.",
            details=exc.details,
        )

    # Generic mapping — preserves code, message, suggestion, and details
    return TdError(
        exc.message,
        code=exc.code,
        suggestion=exc.suggestion or "If this persists, run with TD_DEBUG=1 for more details.",
        details=exc.details,
    )
