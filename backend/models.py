"""SQLAlchemy models for identity and authorization data.

These models define departments, users, roles and permissions. They form
the database foundation for authentication and backend-enforced access.
"""

from datetime import datetime, timezone

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Table,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.database import Base


def current_utc_time() -> datetime:
    """Return the current timezone-aware UTC time.

    Returns:
        The current date and time using the UTC timezone.
    """

    return datetime.now(timezone.utc)


# Connect roles to permissions. A role may have several permissions,
# and the same permission may be granted through several roles.
role_permissions = Table(
    "role_permissions",
    Base.metadata,
    Column(
        "role_id",
        Integer,
        ForeignKey("roles.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "permission_id",
        Integer,
        ForeignKey("permissions.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


# Connect users to roles. Admin may assign several roles to one user,
# and each role may be assigned to several users.
user_roles = Table(
    "user_roles",
    Base.metadata,
    Column(
        "user_id",
        Integer,
        ForeignKey("users.id", ondelete="CASCADE"),
        primary_key=True,
    ),
    Column(
        "role_id",
        Integer,
        ForeignKey("roles.id", ondelete="CASCADE"),
        primary_key=True,
    ),
)


class Department(Base):
    """Represent an organizational department.

    Departments define responsibility boundaries for users, Policy Makers,
    approvals and future internal review records.
    """

    __tablename__ = "departments"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )
    description: Mapped[str | None] = mapped_column(
        String(500),
        nullable=True,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
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

    users: Mapped[list["User"]] = relationship(
        back_populates="department",
    )


class Role(Base):
    """Represent a role assigned to application users.

    Roles group backend permissions. The frontend cannot grant a role by
    submitting a role name; Admin-controlled database assignments are used.
    """

    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True,
    )
    description: Mapped[str] = mapped_column(
        String(300),
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
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

    permissions: Mapped[list["Permission"]] = relationship(
        secondary=role_permissions,
        back_populates="roles",
    )
    users: Mapped[list["User"]] = relationship(
        secondary=user_roles,
        back_populates="roles",
    )


class Permission(Base):
    """Represent one backend-authorized action.

    Permissions use stable codes such as ask_questions, approve_entries
    and manage_users. FastAPI will later enforce them.
    """

    __tablename__ = "permissions"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )
    description: Mapped[str] = mapped_column(
        String(300),
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
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

    roles: Mapped[list[Role]] = relationship(
        secondary=role_permissions,
        back_populates="permissions",
    )


class User(Base):
    """Represent an application user account.

    Attributes:
        id: Unique user identifier.
        username: Unique login name.
        email: Unique email address.
        password_hash: Secure password hash created by the future
            authentication service.
        department_id: Optional assigned department identifier.
        is_active: Whether the account may authenticate.
        last_login_at: UTC time of the latest successful login.
        created_at: UTC account-creation time.
        updated_at: UTC last-modification time.
        department: Related Department object.
        roles: Admin-assigned Role objects.

    Security:
        Plain-text passwords must never be stored in this model. Role and
        department assignments must be managed through authorized backend
        operations rather than trusted from Streamlit.
    """

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )
    email: Mapped[str] = mapped_column(
        String(254),
        unique=True,
        nullable=False,
        index=True,
    )
    password_hash: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )
    department_id: Mapped[int | None] = mapped_column(
        ForeignKey("departments.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=True,
    )
    last_login_at: Mapped[datetime | None] = mapped_column(
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

    department: Mapped[Department | None] = relationship(
        back_populates="users",
    )
    roles: Mapped[list[Role]] = relationship(
        secondary=user_roles,
        back_populates="users",
    )
