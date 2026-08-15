"""Automated tests for the SQLite and SQLAlchemy foundation."""

from collections.abc import Generator
from pathlib import Path

import pytest
from sqlalchemy import Engine, func, inspect, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session, sessionmaker

from backend.database import Base, create_database_engine
from backend.ingestion_models import IngestionRecord
from backend.models import Department, Permission, Role, User


@pytest.fixture
def database_session(
    tmp_path: Path,
) -> Generator[Session, None, None]:
    """Provide an isolated SQLite session for one test.

    Args:
        tmp_path: Pytest-managed temporary directory.

    Yields:
        A SQLAlchemy Session connected to a temporary database.

    Cleanup:
        The session and engine are closed after the test. Pytest removes
        the temporary database directory automatically.
    """

    temporary_database_path = tmp_path / "test_rag_app.db"
    temporary_database_url = f"sqlite:///{temporary_database_path.as_posix()}"

    test_engine = create_database_engine(temporary_database_url)
    Base.metadata.create_all(bind=test_engine)

    test_session_factory = sessionmaker(
        bind=test_engine,
        autoflush=False,
        autocommit=False,
        expire_on_commit=False,
    )

    session = test_session_factory()

    try:
        yield session
    finally:
        session.close()
        test_engine.dispose()


def test_all_foundation_tables_can_be_created(tmp_path: Path) -> None:
    """Verify that every current table can be created together."""

    temporary_database_path = tmp_path / "table_test.db"
    temporary_database_url = f"sqlite:///{temporary_database_path.as_posix()}"

    test_engine: Engine = create_database_engine(
        temporary_database_url,
    )

    try:
        Base.metadata.create_all(bind=test_engine)
        table_names = inspect(test_engine).get_table_names()

        assert table_names == [
            "departments",
            "ingestion_records",
            "permissions",
            "role_permissions",
            "roles",
            "user_roles",
            "users",
        ]
    finally:
        test_engine.dispose()


def test_identity_and_ingestion_record_can_be_saved(
    database_session: Session,
) -> None:
    """Verify a complete linked record can be inserted and retrieved."""

    department = Department(
        name="Policy Operations",
        description="Temporary department used only by this test.",
    )

    permission = Permission(
        code="approve_entries",
        description="Approve eligible internal review entries.",
    )

    policy_maker_role = Role(
        name="policy_maker",
        description="Reviews and decides assigned internal entries.",
        permissions=[permission],
    )

    test_user = User(
        username="test_policy_maker",
        email="policy.maker@example.test",
        # This is a test-only placeholder, not a real password or hash.
        password_hash="test-only-placeholder-hash",
        department=department,
        roles=[policy_maker_role],
    )

    database_session.add(test_user)
    database_session.flush()

    ingestion_record = IngestionRecord(
        reference_number="ING-TEST-0001",
        source_name="Database validation record",
        source_type="validation",
        source_location=None,
        submitted_by_user_id=test_user.id,
        department_id=department.id,
    )

    database_session.add(ingestion_record)
    database_session.commit()

    saved_record = database_session.scalar(
        select(IngestionRecord).where(
            IngestionRecord.reference_number == "ING-TEST-0001"
        )
    )

    assert saved_record is not None
    assert saved_record.approval_status == "pending"
    assert saved_record.processing_status == "awaiting_approval"
    assert saved_record.document_count == 0
    assert saved_record.chunk_count == 0


def test_duplicate_department_is_rolled_back(
    database_session: Session,
) -> None:
    """Verify that a failed duplicate insert can be rolled back safely."""

    database_session.add(
        Department(
            name="Human Resources",
            description="First department record.",
        )
    )
    database_session.commit()

    database_session.add(
        Department(
            name="Human Resources",
            description="Duplicate department record.",
        )
    )

    with pytest.raises(IntegrityError):
        database_session.commit()

    # A failed transaction must be rolled back before the session can
    # perform another database operation.
    database_session.rollback()

    department_count = database_session.scalar(
        select(func.count()).select_from(Department)
    )

    assert department_count == 1
