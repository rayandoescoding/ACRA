import enum
import uuid
from datetime import datetime
from typing import List, Optional, TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text, UUID, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.customer import Customer
    from app.models.order import Order
    from app.models.resolution import Resolution


class TicketPriority(str, enum.Enum):
    """
    Enum representing support ticket priority levels.
    """
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class TicketStatus(str, enum.Enum):
    """
    Enum representing the lifecycle status of a support ticket.
    """
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


class Ticket(Base):
    """
    Ticket database model representing a customer support request.

    Each ticket is always linked to a Customer and optionally to an Order
    when the issue concerns a specific purchase.

    AI-enriched fields (sentiment, intent, ai_summary) are nullable and
    populated asynchronously by the AI agent pipeline — not at creation time.
    """

    __tablename__ = "tickets"

    # -------------------------------------------------------------------------
    # Primary Key
    # -------------------------------------------------------------------------
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    # -------------------------------------------------------------------------
    # Foreign Keys
    # -------------------------------------------------------------------------
    customer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("customers.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    order_id: Mapped[Optional[uuid.UUID]] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("orders.id", ondelete="SET NULL"),
        nullable=True,
        index=True,
    )

    # -------------------------------------------------------------------------
    # Core Fields
    # -------------------------------------------------------------------------
    subject: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    description: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    category: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )

    priority: Mapped[TicketPriority] = mapped_column(
        Enum(
            TicketPriority,
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
        ),
        default=TicketPriority.MEDIUM,
        nullable=False,
    )

    status: Mapped[TicketStatus] = mapped_column(
        Enum(
            TicketStatus,
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
        ),
        default=TicketStatus.OPEN,
        nullable=False,
    )

    # -------------------------------------------------------------------------
    # AI-Enriched Fields
    # -------------------------------------------------------------------------
    sentiment: Mapped[Optional[str]] = mapped_column(
        String(50),
        nullable=True,
    )

    intent: Mapped[Optional[str]] = mapped_column(
        String(100),
        nullable=True,
    )

    ai_summary: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
    )

    # -------------------------------------------------------------------------
    # Timestamps
    # -------------------------------------------------------------------------
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

    # -------------------------------------------------------------------------
    # Relationships
    # -------------------------------------------------------------------------
    customer: Mapped["Customer"] = relationship(
        "Customer",
        back_populates="tickets",
        foreign_keys=[customer_id],
    )

    order: Mapped[Optional["Order"]] = relationship(
        "Order",
        back_populates="tickets",
        foreign_keys=[order_id],
    )

    resolutions: Mapped[List["Resolution"]] = relationship(
        "Resolution",
        back_populates="ticket",
        cascade="all, delete-orphan",
    )
