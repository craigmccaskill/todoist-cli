"""Tests for structured error handling."""

from __future__ import annotations

import json

from td.cli.errors import (
    TdApiError,
    TdAuthError,
    TdError,
    TdNotFoundError,
    TdRateLimitError,
    handle_error,
    map_api_exception,
)
from td.cli.output import OutputMode


class TestTdError:
    def test_json_format(self) -> None:
        err = TdError(
            "Something broke",
            code="TEST_ERROR",
            suggestion="Try again",
            details={"key": "value"},
        )
        data = json.loads(err.format_json())
        assert data["ok"] is False
        assert data["error"]["code"] == "TEST_ERROR"
        assert data["error"]["message"] == "Something broke"
        assert data["error"]["suggestion"] == "Try again"
        assert data["error"]["details"]["key"] == "value"

    def test_plain_format(self) -> None:
        err = TdError("Bad input", suggestion="Check your args")
        text = err.format_plain()
        assert "Bad input" in text
        assert "Check your args" in text

    def test_plain_format_no_suggestion(self) -> None:
        err = TdError("Bad input")
        text = err.format_plain()
        assert "Bad input" in text
        assert "Suggestion" not in text


class TestErrorSubclasses:
    def test_auth_error_defaults(self) -> None:
        err = TdAuthError("No token")
        assert err.code == "AUTH_MISSING"
        assert "td init" in err.suggestion

    def test_not_found_error(self) -> None:
        err = TdNotFoundError(
            "Task not found",
            details={"task_id": "abc123"},
        )
        assert err.code == "TASK_NOT_FOUND"
        assert err.details["task_id"] == "abc123"

    def test_rate_limit_error(self) -> None:
        err = TdRateLimitError("Slow down")
        assert err.code == "API_RATE_LIMIT"
        assert "450" in err.suggestion


class TestHandleError:
    def test_json_mode_writes_to_stderr(self, capsys: object) -> None:
        err = TdError("test error", code="TEST")
        handle_error(err, OutputMode.JSON)
        captured = capsys.readouterr()  # type: ignore[union-attr]
        assert captured.out == ""  # nothing to stdout
        data = json.loads(captured.err)
        assert data["error"]["code"] == "TEST"

    def test_plain_mode_writes_to_stderr(self, capsys: object) -> None:
        err = TdError("test error", suggestion="fix it")
        handle_error(err, OutputMode.PLAIN)
        captured = capsys.readouterr()  # type: ignore[union-attr]
        assert captured.out == ""
        assert "test error" in captured.err

    def test_rich_mode_writes_to_stderr(self, capsys: object) -> None:
        err = TdError("test error", suggestion="fix it")
        handle_error(err, OutputMode.RICH)
        captured = capsys.readouterr()  # type: ignore[union-attr]
        assert captured.out == ""
        assert "test error" in captured.err


class TestMapApiException:
    def _make_status_error(self, status_code: int, reason: str = "") -> Exception:
        """Create an httpx.HTTPStatusError with the given status code."""
        import httpx

        request = httpx.Request("GET", "https://api.todoist.com/rest/v2/tasks")
        response = httpx.Response(status_code, request=request)
        return httpx.HTTPStatusError(
            f"{status_code} {reason}", request=request, response=response
        )

    def test_401_maps_to_auth_error(self) -> None:
        exc = self._make_status_error(401, "Unauthorized")
        result = map_api_exception(exc)
        assert isinstance(result, TdAuthError)
        assert result.code == "AUTH_INVALID"

    def test_404_maps_to_not_found(self) -> None:
        exc = self._make_status_error(404, "Not Found")
        result = map_api_exception(exc)
        assert isinstance(result, TdNotFoundError)

    def test_429_maps_to_rate_limit(self) -> None:
        exc = self._make_status_error(429, "Too Many Requests")
        result = map_api_exception(exc)
        assert isinstance(result, TdRateLimitError)

    def test_500_maps_to_api_error(self) -> None:
        exc = self._make_status_error(500, "Internal Server Error")
        result = map_api_exception(exc)
        assert isinstance(result, TdApiError)

    def test_unknown_exception(self) -> None:
        result = map_api_exception(ValueError("weird"))
        assert isinstance(result, TdApiError)
        assert "weird" in result.message
