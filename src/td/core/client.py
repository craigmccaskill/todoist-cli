"""Todoist API client construction."""

from __future__ import annotations

from todoist_api_python.api import TodoistAPI

from td.core.config import resolve_token
from td.core.exceptions import AuthError
from td.core.rate_limit import create_monitored_client


def get_client() -> TodoistAPI:
    """Construct a TodoistAPI client from the resolved token.

    Raises AuthError if no token is available.
    Uses a monitored httpx client to capture rate limit headers.
    """
    token = resolve_token()
    if not token:
        raise AuthError
    return TodoistAPI(token, client=create_monitored_client())
