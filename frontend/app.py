"""Streamlit entry point for the LangChain RAG frontend.

Functionality 0 provides only the application foundation. Communication
with FastAPI and the system-status display will be added in Functionality 1.
"""

import streamlit as st

from backend.config import get_settings


def render_app() -> None:
    """Render the basic Streamlit application page.

    The page confirms that the frontend can start and read safe application
    configuration. It does not call the backend or access the database.

    Security:
        The page displays only the application name. It does not display
        environment variables, file paths, database details or API keys.
    """

    # Load the same validated configuration used by the backend.
    # This keeps the application name consistent across both layers.
    settings = get_settings()

    # Page configuration must be the first Streamlit page command.
    st.set_page_config(
        page_title=settings.app_name,
        page_icon="🔎",
        layout="wide",
    )

    st.title(settings.app_name)
    st.write("Frontend foundation is running successfully.")

    # Backend connectivity belongs to Functionality 1. This message makes
    # the current limitation clear instead of pretending it is connected.
    st.info(
        "Backend status integration will be added in "
        "Functionality 1 — Health and System Status."
    )


if __name__ == "__main__":
    # Streamlit executes this file as a script. This guard keeps the startup
    # behaviour explicit and makes the render function easier to test later.
    render_app()
