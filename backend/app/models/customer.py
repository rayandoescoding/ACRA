import enum
import uuid
from datetime import datetime
from typing import List, Optional, TYPE_CHECKING

from sqlalchemy import DateTime, Enum, String, UUID, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.account import Account
    from app.models.order import Order
    from app.models.ticket import Ticket


class CustomerTier(str, enum.Enum):
    """
    Enum representing customer subscription tiers.
    """
    STANDARD = "standard"
    PREMIUM = "premium"
    VIP = "vip"


class Customer(Base):
    """
    Customer database model representing client personal info and tier.
    """
    __tablename__ = "customers"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        index=True,
        nullable=False,
    )
    phone: Mapped[Optional[str]] = mapped_column(String(50), nullable=True)
    tier: Mapped[CustomerTier] = mapped_column(
        Enum(CustomerTier),
        default=CustomerTier.STANDARD,
        nullable=False,
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        default=datetime.utcnow,
        nullable=False,
    )

    # Relationships
    account: Mapped[Optional["Account"]] = relationship(
        "Account",
        back_populates="customer",
        uselist=False,
        cascade="all, delete-orphan",
    )
    orders: Mapped[List["Order"]] = relationship(
        "Order",
        back_populates="customer",
        cascade="all, delete-orphan",
    )
    tickets: Mapped[List["Ticket"]] = relationship(
        "Ticket",
        back_populates="customer",
        cascade="all, delete-orphan",
    )
