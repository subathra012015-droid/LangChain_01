"""Automated tests for frontend health-check helpers."""

from unittest.mock import Mock, patch

import requests

from frontend.app import fetch_backend_health, format_status


def test_fetch_backend_health_returns_valid_data() -> None:
    """Verify successful health retrieval from the backend.

    The HTTP request is mocked, so this test does not require FastAPI
    or an internet connection to be running.
    """

    expected_health_data = {
        "status": "healthy",
        "application": "LangChain RAG Application",
        "environment": "development",
        "backend": "available",
        "database": "available",
        "faiss": "not_configured",
        "langsmith": "not_configured",
    }

    mock_response = Mock()
    mock_response.raise_for_status.return_value = None
    mock_response.json.return_value = expected_health_data

    # Replace requests.get only during this test. This makes the test fast,
    # repeatable and independent of a running FastAPI server.
    with patch(
        "frontend.app.requests.get",
        return_value=mock_response,
    ) as mock_get:
        health_data, error_message = fetch_backend_health(
            "http://127.0.0.1:8000/",
        )

    assert health_data == expected_health_data
    assert error_message is None
    mock_get.assert_called_once_with(
        "http://127.0.0.1:8000/health",
        timeout=5.0,
    )


def test_fetch_backend_health_handles_unavailable_backend() -> None:
    """Verify that a connection failure returns a safe message.

    The frontend must not crash or expose raw network exceptions when
    FastAPI is unavailable.
    """

    with patch(
        "frontend.app.requests.get",
        side_effect=requests.exceptions.ConnectionError,
    ):
        health_data, error_message = fetch_backend_health(
            "http://127.0.0.1:8000",
        )

    assert health_data is None
    assert error_message == (
        "Backend unavailable. Start the FastAPI server and try again."
    )


def test_format_status_returns_readable_labels() -> None:
    """Verify conversion of internal statuses into display labels."""

    assert format_status("available") == "Available"
    assert format_status("not_configured") == "Not configured"
    assert format_status("unavailable") == "Unavailable"
    assert format_status("unexpected") == "Unknown"
