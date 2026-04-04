"""Todoist API client construction."""

from __future__ import annotations

from todoist_api_python.api import TodoistAPI

from td.core.config import resolve_token
from td.core.rate_limit import create_monitored_client


class TdAuthError(Exception):
    """Raised when no API token is available."""

    def __init__(self) -> None:
        super().__init__("No API token configured. Run `td init` or set TD_API_TOKEN.")


def get_client() -> TodoistAPI:
    """Construct a TodoistAPI client from the resolved token.

    Raises TdAuthError if no token is available.
    Uses a monitored httpx client to capture rate limit headers.
    """
    token = resolve_token()
    if not token:
        raise TdAuthError
    return TodoistAPI(token, client=create_monitored_client())
