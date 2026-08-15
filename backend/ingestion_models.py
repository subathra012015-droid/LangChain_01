"""SQLAlchemy models for controlled content ingestion.

Ingestion records track content from submission through Policy Maker
approval and eventual FAISS indexing. These records are internal and
must not be exposed through customer-facing API responses.
"""

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from backend.database import Base
from backend.models import current_utc_time


class IngestionRecord(Base):
    """Track one controlled content-ingestion operation.

    Attributes:
        id: Internal numeric identifier.
        reference_number: Unique internal tracking reference.
        source_name: Human-readable source name.
        source_type: Source format, such as user_text, pdf or website.
        source_location: Controlled source reference or stored file path.
        submitted_by_user_id: User who submitted the content.
        department_id: Department responsible for reviewing the content.
        approval_status: Pending, approved or rejected review state.
        reviewed_by_user_id: Policy Maker who made the decision.
        reviewed_at: UTC decision timestamp.
        rejection_reason: Internal structured rejection explanation.
        processing_status: Current ingestion and indexing stage.
        document_count: Number of LangChain Documents loaded.
        chunk_count: Number of chunks generated.
        error_message: Safe internal processing-error summary.
        indexed_at: UTC time at which approved content entered FAISS.
        created_at: UTC record-creation time.
        updated_at: UTC latest-modification time.

    Security:
        This is an internal workflow record. Customer-facing schemas must
        not expose reviewer identity, rejection details, internal paths,
        errors or processing metadata.

    Approval:
        Future service logic will enforce that the submitting user cannot
        approve their own submission.
    """

    __tablename__ = "ingestion_records"

    id: Mapped[int] = mapped_column(primary_key=True)

    reference_number: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
    )

    source_name: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    source_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        index=True,
    )

    source_location: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )

    submitted_by_user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    department_id: Mapped[int] = mapped_column(
        ForeignKey("departments.id", ondelete="RESTRICT"),
        nullable=False,
        index=True,
    )

    approval_status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="pending",
        index=True,
    )

    reviewed_by_user_id: Mapped[int | None] = mapped_column(
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    reviewed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    rejection_reason: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )

    processing_status: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        default="awaiting_approval",
        index=True,
    )

    document_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    chunk_count: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
    )

    error_message: Mapped[str | None] = mapped_column(
        String(1000),
        nullable=True,
    )

    indexed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=current_utc_time,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False,
        default=current_utc_time,
        onupdate=current_utc_time,
    )
