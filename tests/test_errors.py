"""Tests for structured error handling."""

from __future__ import annotations

import json

from td.cli.errors import (
    API_FORBIDDEN,
    API_SERVER_ERROR,
    API_TIMEOUT,
    NETWORK_ERROR,
    TdApiError,
    TdAuthError,
    TdCacheError,
    TdError,
    TdForbiddenError,
    TdNetworkError,
    TdNotFoundError,
    TdProjectNotFoundError,
    TdRateLimitError,
    TdServerError,
    TdTimeoutError,
    TdValidationError,
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

    def test_json_envelope_always_has_required_fields(self) -> None:
        """Every JSON error must include ok, error.code, error.message, error.suggestion."""
        err = TdError("minimal error")
        data = json.loads(err.format_json())
        assert data["ok"] is False
        error = data["error"]
        assert "code" in error
        assert "message" in error
        assert "suggestion" in error
        assert "details" in error

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

    def test_forbidden_error_defaults(self) -> None:
        err = TdForbiddenError("No access")
        assert err.code == API_FORBIDDEN
        assert "permissions" in err.suggestion.lower()

    def test_timeout_error_defaults(self) -> None:
        err = TdTimeoutError("Timed out")
        assert err.code == API_TIMEOUT
        assert "internet" in err.suggestion.lower() or "try again" in err.suggestion.lower()

    def test_server_error_defaults(self) -> None:
        err = TdServerError("Server down")
        assert err.code == API_SERVER_ERROR
        assert "try again" in err.suggestion.lower()

    def test_network_error_defaults(self) -> None:
        err = TdNetworkError("No connection")
        assert err.code == NETWORK_ERROR
        assert "internet" in err.suggestion.lower()

    def test_cache_error(self) -> None:
        err = TdCacheError("Cache corrupt", suggestion="Delete cache and retry.")
        assert err.code == "CACHE_ERROR"
        assert err.suggestion == "Delete cache and retry."

    def test_project_not_found_error(self) -> None:
        err = TdProjectNotFoundError("Project 'X' not found")
        assert err.code == "PROJECT_NOT_FOUND"
        assert "td projects" in err.suggestion


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
    def _make_status_error(self, status_code: int, reason: str = "", body: str = "") -> Exception:
        """Create an httpx.HTTPStatusError with the given status code."""
        import httpx

        request = httpx.Request("GET", "https://api.todoist.com/rest/v2/tasks")
        response = httpx.Response(status_code, request=request, text=body)
        return httpx.HTTPStatusError(f"{status_code} {reason}", request=request, response=response)

    def test_401_maps_to_auth_error(self) -> None:
        exc = self._make_status_error(401, "Unauthorized")
        result = map_api_exception(exc)
        assert isinstance(result, TdAuthError)
        assert result.code == "AUTH_INVALID"

    def test_403_maps_to_forbidden(self) -> None:
        exc = self._make_status_error(403, "Forbidden")
        result = map_api_exception(exc)
        assert isinstance(result, TdForbiddenError)
        assert result.code == API_FORBIDDEN
        assert "permission" in result.suggestion.lower()

    def test_404_maps_to_not_found(self) -> None:
        exc = self._make_status_error(404, "Not Found")
        result = map_api_exception(exc)
        assert isinstance(result, TdNotFoundError)
        assert result.suggestion != ""

    def test_404_extracts_detail(self) -> None:
        exc = self._make_status_error(404, "Not Found", body="Task not found")
        result = map_api_exception(exc)
        assert isinstance(result, TdNotFoundError)
        assert "Task not found" in result.message

    def test_408_maps_to_timeout(self) -> None:
        exc = self._make_status_error(408, "Request Timeout")
        result = map_api_exception(exc)
        assert isinstance(result, TdTimeoutError)
        assert result.code == API_TIMEOUT
        assert "try again" in result.suggestion.lower()

    def test_429_maps_to_rate_limit(self) -> None:
        exc = self._make_status_error(429, "Too Many Requests")
        result = map_api_exception(exc)
        assert isinstance(result, TdRateLimitError)

    def test_400_maps_to_validation_error(self) -> None:
        exc = self._make_status_error(400, "Bad Request")
        result = map_api_exception(exc)
        assert isinstance(result, TdValidationError)
        assert result.code == "VALIDATION_ERROR"
        assert "--help" in result.suggestion

    def test_400_extracts_json_error_message(self) -> None:
        exc = self._make_status_error(400, "Bad Request", body='{"error": "Invalid due date"}')
        result = map_api_exception(exc)
        assert isinstance(result, TdValidationError)
        assert "Invalid due date" in result.message

    def test_400_extracts_plain_text_body(self) -> None:
        exc = self._make_status_error(400, "Bad Request", body="Missing required field")
        result = map_api_exception(exc)
        assert isinstance(result, TdValidationError)
        assert "Missing required field" in result.message

    def test_500_maps_to_server_error(self) -> None:
        exc = self._make_status_error(500, "Internal Server Error")
        result = map_api_exception(exc)
        assert isinstance(result, TdServerError)
        assert result.code == API_SERVER_ERROR
        assert "try again" in result.suggestion.lower()

    def test_500_extracts_response_body(self) -> None:
        exc = self._make_status_error(500, "Server Error", body='{"error": "DB timeout"}')
        result = map_api_exception(exc)
        assert "DB timeout" in result.message

    def test_502_maps_to_server_error(self) -> None:
        exc = self._make_status_error(502, "Bad Gateway")
        result = map_api_exception(exc)
        assert isinstance(result, TdServerError)
        assert "bad gateway" in result.message.lower()
        assert "try again" in result.suggestion.lower()

    def test_503_maps_to_server_error(self) -> None:
        exc = self._make_status_error(503, "Service Unavailable")
        result = map_api_exception(exc)
        assert isinstance(result, TdServerError)
        assert "unavailable" in result.message.lower()
        assert "status.todoist.com" in result.suggestion

    def test_504_maps_to_server_error(self) -> None:
        exc = self._make_status_error(504, "Gateway Timeout")
        result = map_api_exception(exc)
        assert isinstance(result, TdServerError)
        assert "gateway timed out" in result.message.lower()
        assert "try again" in result.suggestion.lower()

    def test_unknown_http_status_fallback(self) -> None:
        exc = self._make_status_error(418, "I'm a teapot")
        result = map_api_exception(exc)
        assert isinstance(result, TdApiError)
        assert result.details.get("status_code") == 418
        assert "status.todoist.com" in result.suggestion

    def test_unknown_exception(self) -> None:
        result = map_api_exception(ValueError("weird"))
        assert isinstance(result, TdApiError)
        assert "weird" in result.message
        assert "TD_DEBUG" in result.suggestion

    def test_connect_timeout(self) -> None:
        import httpx

        exc = httpx.ConnectTimeout("Connection timed out")
        result = map_api_exception(exc)
        assert isinstance(result, TdTimeoutError)
        assert "connection" in result.message.lower()
        assert "internet" in result.suggestion.lower()

    def test_read_timeout(self) -> None:
        import httpx

        exc = httpx.ReadTimeout("Read timed out")
        result = map_api_exception(exc)
        assert isinstance(result, TdTimeoutError)
        assert "timed out" in result.message.lower()

    def test_connect_error(self) -> None:
        import httpx

        exc = httpx.ConnectError("Connection refused")
        result = map_api_exception(exc)
        assert isinstance(result, TdNetworkError)
        assert "connect" in result.message.lower()
        assert "internet" in result.suggestion.lower()

    def test_generic_timeout_exception(self) -> None:
        import httpx

        exc = httpx.PoolTimeout("Pool timed out")
        result = map_api_exception(exc)
        assert isinstance(result, TdTimeoutError)
        assert "timed out" in result.message.lower()


class TestMapCoreException:
    def test_auth_error_maps_to_td_auth_error(self) -> None:
        from td.core.exceptions import AuthError

        exc = AuthError()
        result = map_core_exception(exc)
        assert isinstance(result, TdAuthError)
        assert "td init" in result.suggestion

    def test_project_not_found_maps_to_td_project_not_found(self) -> None:
        from td.core.exceptions import ProjectNotFoundError

        exc = ProjectNotFoundError(
            "Project 'foo' not found",
            suggestion="Did you mean: bar?",
            details={"query": "foo"},
        )
        result = map_core_exception(exc)
        assert isinstance(result, TdProjectNotFoundError)
        assert result.code == "PROJECT_NOT_FOUND"
        assert result.message == "Project 'foo' not found"
        assert result.suggestion == "Did you mean: bar?"
        assert result.details["query"] == "foo"

    def test_project_not_found_default_suggestion(self) -> None:
        from td.core.exceptions import ProjectNotFoundError

        exc = ProjectNotFoundError("Project 'x' not found")
        result = map_core_exception(exc)
        assert isinstance(result, TdProjectNotFoundError)
        assert "td projects" in result.suggestion

    def test_section_not_found_maps_correctly(self) -> None:
        from td.core.exceptions import SectionNotFoundError

        exc = SectionNotFoundError("Section 'x' not found")
        result = map_core_exception(exc)
        assert isinstance(result, TdNotFoundError)
        assert result.code == "SECTION_NOT_FOUND"
        assert "td sections" in result.suggestion

    def test_label_not_found_maps_correctly(self) -> None:
        from td.core.exceptions import LabelNotFoundError

        exc = LabelNotFoundError("Label 'x' not found")
        result = map_core_exception(exc)
        assert isinstance(result, TdNotFoundError)
        assert result.code == "LABEL_NOT_FOUND"
        assert "td labels" in result.suggestion

    def test_generic_core_error(self) -> None:
        from td.core.exceptions import TdCoreError

        exc = TdCoreError("something broke", code="CUSTOM")
        result = map_core_exception(exc)
        assert isinstance(result, TdError)
        assert result.code == "CUSTOM"

    def test_generic_core_error_has_suggestion(self) -> None:
        from td.core.exceptions import TdCoreError

        exc = TdCoreError("something broke", code="CUSTOM")
        result = map_core_exception(exc)
        assert result.suggestion != ""

    def test_non_core_exception_has_suggestion(self) -> None:
        exc = RuntimeError("unexpected")
        result = map_core_exception(exc)
        assert isinstance(result, TdApiError)
        assert "TD_DEBUG" in result.suggestion


class TestJsonEnvelopeConsistency:
    """Verify that all error types produce consistent JSON envelopes."""

    def _check_envelope(self, err: TdError) -> None:
        data = json.loads(err.format_json())
        assert data["ok"] is False
        error = data["error"]
        assert isinstance(error["code"], str) and len(error["code"]) > 0
        assert isinstance(error["message"], str) and len(error["message"]) > 0
        assert isinstance(error["suggestion"], str)
        assert isinstance(error["details"], dict)

    def test_auth_error_envelope(self) -> None:
        self._check_envelope(TdAuthError("No token"))

    def test_not_found_error_envelope(self) -> None:
        self._check_envelope(TdNotFoundError("Not found"))

    def test_validation_error_envelope(self) -> None:
        self._check_envelope(TdValidationError("Bad input"))

    def test_rate_limit_error_envelope(self) -> None:
        self._check_envelope(TdRateLimitError("Slow down"))

    def test_forbidden_error_envelope(self) -> None:
        self._check_envelope(TdForbiddenError("No access"))

    def test_timeout_error_envelope(self) -> None:
        self._check_envelope(TdTimeoutError("Timed out"))

    def test_server_error_envelope(self) -> None:
        self._check_envelope(TdServerError("Server error"))

    def test_network_error_envelope(self) -> None:
        self._check_envelope(TdNetworkError("No connection"))

    def test_cache_error_envelope(self) -> None:
        self._check_envelope(TdCacheError("Corrupt cache"))

    def test_project_not_found_error_envelope(self) -> None:
        self._check_envelope(TdProjectNotFoundError("No project"))
