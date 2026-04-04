"""Tests for structured error handling."""

from __future__ import annotations

import json
from unittest.mock import MagicMock

from td.cli.errors import (
    TdApiError,
    TdAuthError,
    TdError,
    TdNotFoundError,
    TdRateLimitError,
    handle_error,
    map_api_exception,
    map_core_exception,
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
    def test_401_maps_to_auth_error(self) -> None:
        from requests import HTTPError

        resp = MagicMock()
        resp.status_code = 401
        exc = HTTPError(response=resp)
        result = map_api_exception(exc)
        assert isinstance(result, TdAuthError)
        assert result.code == "AUTH_INVALID"

    def test_404_maps_to_not_found(self) -> None:
        from requests import HTTPError

        resp = MagicMock()
        resp.status_code = 404
        exc = HTTPError(response=resp)
        result = map_api_exception(exc)
        assert isinstance(result, TdNotFoundError)

    def test_429_maps_to_rate_limit(self) -> None:
        from requests import HTTPError

        resp = MagicMock()
        resp.status_code = 429
        exc = HTTPError(response=resp)
        result = map_api_exception(exc)
        assert isinstance(result, TdRateLimitError)

    def test_500_maps_to_api_error(self) -> None:
        from requests import HTTPError

        resp = MagicMock()
        resp.status_code = 500
        resp.reason = "Internal Server Error"
        exc = HTTPError(response=resp)
        result = map_api_exception(exc)
        assert isinstance(result, TdApiError)

    def test_unknown_exception(self) -> None:
        result = map_api_exception(ValueError("weird"))
        assert isinstance(result, TdApiError)
        assert "weird" in result.message


class TestMapCoreException:
    def test_auth_error_maps_to_td_auth_error(self) -> None:
        from td.core.exceptions import AuthError

        exc = AuthError()
        result = map_core_exception(exc)
        assert isinstance(result, TdAuthError)
        assert "td init" in result.suggestion

    def test_project_not_found_preserves_fields(self) -> None:
        from td.core.exceptions import ProjectNotFoundError

        exc = ProjectNotFoundError(
            "Project 'foo' not found",
            suggestion="Did you mean: bar?",
            details={"query": "foo"},
        )
        result = map_core_exception(exc)
        assert isinstance(result, TdError)
        assert result.code == "PROJECT_NOT_FOUND"
        assert result.message == "Project 'foo' not found"
        assert result.suggestion == "Did you mean: bar?"
        assert result.details["query"] == "foo"

    def test_generic_core_error(self) -> None:
        from td.core.exceptions import TdCoreError

        exc = TdCoreError("something broke", code="CUSTOM")
        result = map_core_exception(exc)
        assert isinstance(result, TdError)
        assert result.code == "CUSTOM"
