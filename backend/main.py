"""FastAPI entry point for the LangChain RAG backend.

Functionality 2 initializes the SQLite foundation during application
startup and reports actual database readiness through the health endpoint.
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from sqlalchemy.exc import SQLAlchemyError

from backend.config import get_settings
from backend.database import (
    check_database_connection,
    initialize_database,
)
from backend.schemas import HealthResponse

# Create a module logger for safe operational messages.
# Detailed database credentials and connection strings are never logged.
logger = logging.getLogger(__name__)


# Load validated configuration once during application startup.
settings = get_settings()


@asynccontextmanager
async def application_lifespan(
    application: FastAPI,
) -> AsyncIterator[None]:
    """Initialize and close application-level resources.

    Args:
        application: The FastAPI application being started.

    Yields:
        Control to FastAPI while the application is running.

    Startup behaviour:
        - Create missing database tables.
        - Preserve existing tables and records.
        - Perform a lightweight connection check.
        - Store only a Boolean readiness result.

    Failure behaviour:
        The backend remains available and reports degraded health. Raw
        database exceptions and connection details are not exposed.
    """

    # Start conservatively. The value becomes True only after table
    # initialization and a successful connection check.
    application.state.database_available = False

    try:
        initialize_database()
        application.state.database_available = check_database_connection()
    except SQLAlchemyError:
        # Keep the message generic to avoid exposing a database URL,
        # local path or future credentials.
        logger.error("Database initialization failed.")
        application.state.database_available = False

    yield

    # SQLite connections are managed by SQLAlchemy's engine and session
    # pools. No application-wide session is kept open here.


# Create FastAPI with the recommended lifespan mechanism.
app = FastAPI(
    title=settings.app_name,
    description="Backend API for the LangChain RAG application.",
    version="0.3.0",
    lifespan=application_lifespan,
)


@app.get("/", tags=["System"])
def read_root() -> dict[str, str]:
    """Return a basic response proving that the backend is running.

    Returns:
        A dictionary containing a safe status message.
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

    Database behaviour:
        Database readiness is established during application startup.
        The health request reads the stored Boolean result and does not
        run the full test suite or recreate tables.

    Security:
        The response excludes database URLs, paths, credentials,
        exceptions and table contents.
    """

    database_is_available = bool(getattr(app.state, "database_available", False))

    return HealthResponse(
        status="healthy" if database_is_available else "degraded",
        application=settings.app_name,
        environment=settings.app_env,
        backend="available",
        database=("available" if database_is_available else "unavailable"),
        faiss="not_configured",
        langsmith="not_configured",
    )
