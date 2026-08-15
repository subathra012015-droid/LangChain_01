"""Pydantic schemas used by the FastAPI backend.

Schemas define and validate the shape of information returned by API
endpoints. They help keep API responses predictable for the frontend.
"""

from typing import Literal

from pydantic import BaseModel, Field

# These type aliases limit status fields to known values.
# A spelling mistake or unsupported status will fail validation.
ApplicationStatus = Literal["healthy", "degraded", "unhealthy"]
ComponentStatus = Literal["available", "not_configured", "unavailable"]
EnvironmentName = Literal["development", "testing", "production"]


class HealthResponse(BaseModel):
    """Represent the safe health status returned by the backend.

    Attributes:
        status: Overall application-health classification.
        application: Human-readable application name.
        environment: Dynamically selected runtime environment.
        backend: FastAPI backend availability.
        database: Current SQLite integration status.
        faiss: Current FAISS integration status.
        langsmith: Current LangSmith integration status.

    Security:
        This schema deliberately excludes API keys, database URLs,
        local filesystem paths and detailed internal exceptions.
    """

    status: ApplicationStatus
    application: str = Field(min_length=1)
    environment: EnvironmentName
    backend: ComponentStatus
    database: ComponentStatus
    faiss: ComponentStatus
    langsmith: ComponentStatus
