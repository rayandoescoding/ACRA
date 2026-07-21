import enum
import uuid
from datetime import date
from typing import TYPE_CHECKING

from sqlalchemy import Date, Enum, ForeignKey, String, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.customer import Customer


class AccountStatus(str, enum.Enum):
    """
    Enum representing account statuses.
    """
    ACTIVE = "active"
    SUSPENDED = "suspended"
    CANCELLED = "cancelled"


class Account(Base):
    """
    Account database model representing a customer's subscription plan.
    """
    __tablename__ = "accounts"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    customer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("customers.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    plan_type: Mapped[str] = mapped_column(String(100), nullable=False)
    status: Mapped[AccountStatus] = mapped_column(
    Enum(
        AccountStatus,
        values_callable=lambda enum: [item.value for item in enum],
    ),
    default=AccountStatus.ACTIVE,
    nullable=False,
)
    signup_date: Mapped[date] = mapped_column(Date, nullable=False)
    billing_cycle: Mapped[str] = mapped_column(String(50), nullable=False)

    # Relationships
    customer: Mapped["Customer"] = relationship(
        "Customer",
        back_populates="account",
    )
