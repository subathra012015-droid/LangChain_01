"""Automated tests for the FastAPI system endpoints."""

from fastapi.testclient import TestClient

from backend.main import app

# TestClient calls FastAPI directly without opening a network port.
# These endpoint tests deliberately do not enter the lifespan context,
# preventing creation of the development rag_app.db file.
client = TestClient(app)


EXPECTED_HEALTHY_RESPONSE = {
    "status": "healthy",
    "application": "LangChain RAG Application",
    "environment": "development",
    "backend": "available",
    "database": "available",
    "faiss": "not_configured",
    "langsmith": "not_configured",
}


def test_read_root_returns_successful_response() -> None:
    """Verify that the root endpoint returns its safe response."""

    response = client.get("/")

    assert response.status_code == 200
    assert response.json() == {
        "message": "LangChain RAG Application backend is running."
    }


def test_health_reports_available_database() -> None:
    """Verify healthy status after successful database initialization.

    The Boolean application state is set directly so the endpoint can be
    tested without creating or connecting to the development database.
    """

    app.state.database_available = True

    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == EXPECTED_HEALTHY_RESPONSE


def test_health_reports_degraded_database() -> None:
    """Verify degraded status when database initialization is unavailable."""

    app.state.database_available = False

    response = client.get("/health")
    response_data = response.json()

    assert response.status_code == 200
    assert response_data["status"] == "degraded"
    assert response_data["backend"] == "available"
    assert response_data["database"] == "unavailable"


def test_health_does_not_expose_sensitive_fields() -> None:
    """Verify that health output excludes sensitive configuration."""

    app.state.database_available = True

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
