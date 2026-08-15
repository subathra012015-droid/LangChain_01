"""Streamlit entry point for the LangChain RAG frontend.

Functionality 1 calls the FastAPI health endpoint and displays the safe
system status returned by the backend.
"""

from typing import Any

import requests
import streamlit as st

from backend.config import get_settings


def fetch_backend_health(
    backend_url: str,
    timeout_seconds: float = 5.0,
) -> tuple[dict[str, Any] | None, str | None]:
    """Request the current health status from FastAPI.

    Args:
        backend_url: Base URL of the FastAPI backend.
        timeout_seconds: Maximum number of seconds to wait for a response.

    Returns:
        A tuple containing:
        - The decoded health-response dictionary, or None on failure.
        - A safe user-facing error message, or None on success.

    Security:
        Raw exceptions are not returned because they could reveal internal
        network details or local configuration.
    """

    # Remove a possible trailing slash before adding the endpoint path.
    # This prevents URLs such as http://127.0.0.1:8000//health.
    health_url = f"{backend_url.rstrip('/')}/health"

    try:
        # The timeout prevents Streamlit from waiting indefinitely when
        # FastAPI is stopped or unavailable.
        response = requests.get(
            health_url,
            timeout=timeout_seconds,
        )

        # Convert non-success HTTP responses into controlled exceptions.
        response.raise_for_status()

        health_data = response.json()

        # The frontend expects a JSON object rather than a list or scalar.
        if not isinstance(health_data, dict):
            return None, "The backend returned an unexpected response format."

        return health_data, None

    except requests.exceptions.Timeout:
        return None, "The backend health check timed out."

    except requests.exceptions.ConnectionError:
        return None, "Backend unavailable. Start the FastAPI server and try again."

    except requests.exceptions.JSONDecodeError:
        return None, "The backend returned an invalid JSON response."

    except requests.exceptions.RequestException:
        return None, "The backend health check failed."


def format_status(status: str) -> str:
    """Convert an internal component status into readable display text.

    Args:
        status: Status value returned by the FastAPI health endpoint.

    Returns:
        A human-readable status label.
    """

    status_labels = {
        "available": "Available",
        "not_configured": "Not configured",
        "unavailable": "Unavailable",
    }

    return status_labels.get(status, "Unknown")


def render_system_status(health_data: dict[str, Any]) -> None:
    """Display backend component status in Streamlit.

    Args:
        health_data: Valid health information returned by FastAPI.

    Security:
        Only explicitly selected safe fields are displayed. The function
        does not render the complete response dictionary.
    """

    st.subheader("System status")

    if health_data.get("status") == "healthy":
        st.success("Backend is healthy.")
    elif health_data.get("status") == "degraded":
        st.warning("Backend is running with limited functionality.")
    else:
        st.error("Backend is unhealthy.")

    # Display only known safe fields instead of automatically rendering
    # every value that might appear in a future backend response.
    status_rows = [
        {
            "Component": "Backend",
            "Status": format_status(str(health_data.get("backend", "unknown"))),
        },
        {
            "Component": "Database",
            "Status": format_status(str(health_data.get("database", "unknown"))),
        },
        {
            "Component": "FAISS",
            "Status": format_status(str(health_data.get("faiss", "unknown"))),
        },
        {
            "Component": "LangSmith",
            "Status": format_status(str(health_data.get("langsmith", "unknown"))),
        },
    ]

    st.table(status_rows)
    st.caption(f"Environment: {health_data.get('environment', 'unknown')}")


def render_app() -> None:
    """Render the Streamlit application and backend-health section.

    The function loads safe frontend configuration, requests backend health
    information and handles backend failures without crashing the page.
    """

    settings = get_settings()

    # Page configuration must be the first Streamlit page command.
    st.set_page_config(
        page_title=settings.app_name,
        page_icon="🔎",
        layout="wide",
    )

    st.title(settings.app_name)
    st.write("Frontend foundation is running successfully.")

    health_data, error_message = fetch_backend_health(
        backend_url=str(settings.backend_url),
    )

    if error_message is not None:
        st.error(error_message)
        return

    if health_data is None:
        # This defensive branch protects against unexpected future changes
        # even though the fetch function normally supplies an error message.
        st.error("Backend health information is unavailable.")
        return

    render_system_status(health_data)


if __name__ == "__main__":
    # Streamlit executes this file as a script. Keeping the call inside a
    # main guard also makes the individual functions easier to test.
    render_app()
