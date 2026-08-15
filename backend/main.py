"""FastAPI entry point for the LangChain RAG backend.

Functionality 1 adds a safe health endpoint. Database access, document
ingestion, FAISS retrieval and AI operations will be introduced
individually in later functionalities.
"""

from fastapi import FastAPI

from backend.config import get_settings
from backend.schemas import HealthResponse

# Load the validated configuration once during application startup.
# No secret values are printed or returned to the frontend.
settings = get_settings()


# Create the FastAPI application.
# The application name comes dynamically from .env or the deployment
# environment instead of being hard-coded in this file.
app = FastAPI(
    title=settings.app_name,
    description="Backend API for the LangChain RAG application.",
    version="0.2.0",
)


@app.get("/", tags=["System"])
def read_root() -> dict[str, str]:
    """Return a basic response proving that the backend is running.

    Returns:
        A dictionary containing a safe status message.

    Security:
        This response deliberately excludes environment variables,
        local file paths, database details and API keys.
    """

    return {
        "message": f"{settings.app_name} backend is running.",
    }


@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["System"],
)
def read_health() -> HealthResponse:
    """Return the current foundation-component status.

    Returns:
        A validated HealthResponse containing safe component statuses.

    Current scope:
        The backend is available. SQLite, FAISS and LangSmith are reported
        as not configured because their functionalities have not been
        implemented yet.

    Security:
        The response excludes API keys, connection strings, filesystem
        paths and detailed exception information.
    """

    return HealthResponse(
        status="healthy",
        application=settings.app_name,
        environment=settings.app_env,
        backend="available",
        database="not_configured",
        faiss="not_configured",
        langsmith="not_configured",
    )
