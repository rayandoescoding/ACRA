import enum
import uuid
from decimal import Decimal
from datetime import datetime
from typing import List, Optional, TYPE_CHECKING

from sqlalchemy import DateTime, Enum, ForeignKey, Numeric, String, UUID, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.customer import Customer
    from app.models.ticket import Ticket


class OrderStatus(str, enum.Enum):
    """
    Enum representing order statuses.
    """
    PLACED = "placed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"


class Order(Base):
    """
    Order database model representing a customer's product order.
    """
    __tablename__ = "orders"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )
    customer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("customers.id", ondelete="CASCADE"),
        nullable=False,
    )
    product_name: Mapped[str] = mapped_column(String(255), nullable=False)
    amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(10), default="USD", nullable=False)
    status: Mapped[OrderStatus] = mapped_column(
        Enum(OrderStatus),
        default=OrderStatus.PLACED,
        nullable=False,
    )
    order_date: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        default=datetime.utcnow,
        nullable=False,
    )
    delivery_eta: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)

    # Relationships
    customer: Mapped["Customer"] = relationship(
        "Customer",
        back_populates="orders",
    )
    tickets: Mapped[List["Ticket"]] = relationship(
        "Ticket",
        back_populates="order",
    )
