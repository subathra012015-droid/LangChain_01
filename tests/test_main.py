"""Automated tests for the basic FastAPI application."""

from fastapi.testclient import TestClient

from backend.main import app

# TestClient calls the FastAPI application directly during automated tests.
# It does not require a separately running Uvicorn server.
client = TestClient(app)


def test_read_root_returns_successful_response() -> None:
    """Verify that the root endpoint returns the expected safe response.

    The test confirms:
        - The endpoint accepts a GET request.
        - The HTTP response status is 200.
        - The response contains the expected application message.
        - No environment variables or secrets are included.
    """

    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "message": "LangChain RAG Application backend is running."
    }
