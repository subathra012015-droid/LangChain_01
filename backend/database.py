"""SQLAlchemy database connection and session management.

This module creates the database engine, applies concurrency-friendly
SQLite settings, provides controlled sessions and performs lightweight
connection checks.
"""

from collections.abc import Generator
from typing import Any

from sqlalchemy import Engine, create_engine, event, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from backend.config import get_settings


class Base(DeclarativeBase):
    """Base class inherited by all SQLAlchemy database models."""

    pass


def create_database_engine(database_url: str | None = None) -> Engine:
    """Create a SQLAlchemy engine for the selected database.

    Args:
        database_url: Optional database URL. If omitted, the value is
            loaded dynamically from application configuration.

    Returns:
        A configured SQLAlchemy Engine.

    Concurrency:
        SQLite receives WAL mode, foreign-key enforcement and a five-second
        busy timeout.

    Security:
        The database URL must never be printed because a future production
        URL may contain credentials.
    """

    selected_database_url = database_url or get_settings().database_url
    is_sqlite = selected_database_url.startswith("sqlite")

    connection_arguments: dict[str, Any] = {}

    if is_sqlite:
        connection_arguments = {
            "check_same_thread": False,
            "timeout": 5,
        }

    database_engine = create_engine(
        selected_database_url,
        connect_args=connection_arguments,
        pool_pre_ping=True,
    )

    if is_sqlite:

        @event.listens_for(database_engine, "connect")
        def configure_sqlite_connection(
            database_api_connection: Any,
            connection_record: Any,
        ) -> None:
            """Apply safety and concurrency settings to each connection.

            Args:
                database_api_connection: Raw SQLite connection supplied
                    by SQLAlchemy.
                connection_record: Required SQLAlchemy pool-event record.
            """

            del connection_record

            cursor = database_api_connection.cursor()

            try:
                # Enforce declared foreign-key relationships.
                cursor.execute("PRAGMA foreign_keys=ON")

                # Allow reads to continue while a write is active.
                cursor.execute("PRAGMA journal_mode=WAL")

                # Wait briefly when another write holds the database lock.
                cursor.execute("PRAGMA busy_timeout=5000")
            finally:
                cursor.close()

    return database_engine


# Configure the application database engine without creating tables.
engine = create_database_engine()


# Create independent sessions for separate requests and users.
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


def initialize_database() -> None:
    """Create registered tables that do not already exist.

    This function imports every model module before calling create_all(),
    ensuring SQLAlchemy knows about identity and ingestion tables.

    Existing tables and rows are preserved.

    Raises:
        SQLAlchemyError: If database initialization fails.
    """

    # Register identity and authorization tables.
    import backend.models  # noqa: F401

    # Register controlled-ingestion tables.
    import backend.ingestion_models  # noqa: F401

    Base.metadata.create_all(bind=engine)


def check_database_connection(
    database_engine: Engine | None = None,
) -> bool:
    """Perform a lightweight database-availability check.

    Args:
        database_engine: Optional engine to check. If omitted, the
            application engine is used.

    Returns:
        True when the database accepts a simple query; otherwise False.

    Security:
        Raw exceptions and connection details are not returned.
    """

    selected_engine = database_engine or engine

    try:
        with selected_engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        return True
    except SQLAlchemyError:
        return False


def get_database_session() -> Generator[Session, None, None]:
    """Provide an independent database session and always close it.

    Yields:
        An active SQLAlchemy Session for one controlled operation.

    Transaction handling:
        Service functions will explicitly commit successful changes and
        roll back failures. This function guarantees session closure.
    """

    database_session = SessionLocal()

    try:
        yield database_session
    finally:
        database_session.close()
