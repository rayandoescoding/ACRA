"""Authentication user model independent from customer domain records."""

import enum
import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, String, UUID, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class UserRole(str, enum.Enum):
    """Roles available to authenticated internal users."""

    ADMIN = "admin"
    SUPPORT_AGENT = "support_agent"


class User(Base):
    """Internal application identity used for authentication and authorization."""

    __tablename__ = "users"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        Enum(UserRole, name="userrole"),
        default=UserRole.SUPPORT_AGENT,
        nullable=False,
    )
    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        default=datetime.utcnow,
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=datetime.utcnow,
        default=datetime.utcnow,
        nullable=False,
    )
