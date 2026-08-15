"""Automated tests for the FastAPI system endpoints."""

from fastapi.testclient import TestClient

from backend.main import app

# TestClient calls FastAPI directly without opening a network port or
# requiring a separately running Uvicorn server.
client = TestClient(app)


# Keep the expected health response in one place so the test remains
# readable and any intentional future status change is easy to identify.
EXPECTED_HEALTH_RESPONSE = {
    "status": "healthy",
    "application": "LangChain RAG Application",
    "environment": "development",
    "backend": "available",
    "database": "not_configured",
    "faiss": "not_configured",
    "langsmith": "not_configured",
}


def test_read_root_returns_successful_response() -> None:
    """Verify that the root endpoint returns the expected safe response.

    The test confirms:
        - The endpoint accepts a GET request.
        - The HTTP response status is 200.
        - The response contains the expected application message.
    """

    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "message": "LangChain RAG Application backend is running."
    }


def test_health_returns_expected_component_statuses() -> None:
    """Verify that the health endpoint reports current component statuses.

    The test confirms that the backend is available while components not
    yet implemented remain clearly marked as not configured.
    """

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == EXPECTED_HEALTH_RESPONSE


def test_health_does_not_expose_sensitive_fields() -> None:
    """Verify that the health response excludes sensitive configuration.

    The check protects against accidentally returning secrets, database
    connection strings, authorization values or internal filesystem paths.
    """

    response = client.get("/health")
    response_fields = set(response.json().keys())

    forbidden_fields = {
        "openai_api_key",
        "langsmith_api_key",
        "database_url",
        "env_file_path",
        "authorization",
        "password",
        "secret",
    }

    assert response.status_code == 200
    assert response_fields.isdisjoint(forbidden_fields)
