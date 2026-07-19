"""Typed business-context records used before downstream AI planning."""

from dataclasses import dataclass
from datetime import date, datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from app.models.account import AccountStatus
from app.models.customer import CustomerTier
from app.models.order import OrderStatus
from app.models.resolution import ResolutionStatus
from app.models.ticket import TicketPriority, TicketStatus


@dataclass(frozen=True, slots=True)
class CustomerProfile:
    """Stable customer facts relevant to ticket handling."""

    id: UUID
    full_name: str
    email: str
    phone: Optional[str]
    tier: CustomerTier
    created_at: datetime


@dataclass(frozen=True, slots=True)
class CustomerAccount:
    """Customer subscription and account status context."""

    id: UUID
    customer_id: UUID
    plan_type: str
    status: AccountStatus
    signup_date: date
    billing_cycle: str


@dataclass(frozen=True, slots=True)
class CustomerOrder:
    """A customer order retained for contextual retrieval."""

    id: UUID
    customer_id: UUID
    product_name: str
    amount: Decimal
    currency: str
    status: OrderStatus
    order_date: datetime
    delivery_eta: Optional[datetime]


@dataclass(frozen=True, slots=True)
class TicketMetadata:
    """Ticket information supplied to later planning stages."""

    id: UUID
    customer_id: UUID
    order_id: Optional[UUID]
    subject: str
    description: Optional[str]
    category: Optional[str]
    priority: TicketPriority
    status: TicketStatus
    sentiment: Optional[str]
    intent: Optional[str]
    ai_summary: Optional[str]
    created_at: datetime
    updated_at: datetime


@dataclass(frozen=True, slots=True)
class PreviousResolution:
    """A historical resolution linked to a previous customer ticket."""

    id: UUID
    ticket_id: UUID
    generated_response: Optional[str]
    confidence_score: Optional[float]
    escalation_required: bool
    resolution_status: ResolutionStatus
    model_name: Optional[str]
    created_at: datetime


@dataclass(frozen=True, slots=True)
class ContextPackage:
    """Single immutable package of relational business context for one ticket.

    The package holds typed relational data only. Future RAG sources can be
    added as new fields or companion source records without changing the
    existing customer and ticket context contract.
    """

    ticket: TicketMetadata
    customer: CustomerProfile
    account: Optional[CustomerAccount]
    orders: tuple[CustomerOrder, ...]
    previous_tickets: tuple[TicketMetadata, ...]
    previous_resolutions: tuple[PreviousResolution, ...]
    priority: TicketPriority
    sentiment: Optional[str]
    intent: Optional[str]
    source: str = "relational_database"
