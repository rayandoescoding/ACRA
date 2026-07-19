"""Asynchronous relational context retrieval for ticket processing."""

from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.base import AgentResult, BaseAgent
from app.agents.context_builder import ContextBuilder
from app.agents.context_models import (
    ContextPackage,
    CustomerAccount,
    CustomerOrder,
    CustomerProfile,
    PreviousResolution,
    TicketMetadata,
)
from app.models.account import Account
from app.models.customer import Customer
from app.models.order import Order
from app.models.resolution import Resolution
from app.models.ticket import Ticket


class ContextTicketNotFoundError(LookupError):
    """Raised when context retrieval is requested for a missing ticket."""

    def __init__(self, ticket_id: UUID) -> None:
        self.ticket_id = ticket_id
        super().__init__(f"Ticket '{ticket_id}' was not found for context retrieval.")


class ContextCustomerNotFoundError(LookupError):
    """Raised when a ticket's required customer record is unavailable."""

    def __init__(self, customer_id: UUID) -> None:
        self.customer_id = customer_id
        super().__init__(f"Customer '{customer_id}' was not found for context retrieval.")


class ContextRetrievalAgent(BaseAgent[UUID, ContextPackage]):
    """Retrieves customer-scoped relational context for a ticket asynchronously."""

    def __init__(
        self,
        session: AsyncSession,
        *,
        builder: ContextBuilder | None = None,
        max_orders: int = 50,
        max_previous_tickets: int = 50,
        max_previous_resolutions: int = 50,
    ) -> None:
        self._validate_limit("max_orders", max_orders)
        self._validate_limit("max_previous_tickets", max_previous_tickets)
        self._validate_limit("max_previous_resolutions", max_previous_resolutions)
        self._session = session
        self._builder = builder or ContextBuilder()
        self._max_orders = max_orders
        self._max_previous_tickets = max_previous_tickets
        self._max_previous_resolutions = max_previous_resolutions

    async def execute(self, input_data: UUID) -> AgentResult[ContextPackage]:
        """Retrieve and package business context for a ticket identifier."""
        context = await self.retrieve_context(input_data)
        return AgentResult(value=context)

    async def retrieve_context(self, ticket_id: UUID) -> ContextPackage:
        """Build one context package using async relational database queries."""
        ticket = await self._session.get(Ticket, ticket_id)
        if ticket is None:
            raise ContextTicketNotFoundError(ticket_id)

        customer = await self._session.get(Customer, ticket.customer_id)
        if customer is None:
            raise ContextCustomerNotFoundError(ticket.customer_id)

        account = await self._session.scalar(
            select(Account).where(Account.customer_id == customer.id)
        )
        orders = await self._load_orders(customer.id)
        previous_tickets = await self._load_previous_tickets(customer.id, ticket.id)
        previous_resolutions = await self._load_previous_resolutions(
            customer.id,
            ticket.id,
        )

        return await self._builder.build(
            ticket=self._ticket_metadata(ticket),
            customer=self._customer_profile(customer),
            account=self._customer_account(account) if account is not None else None,
            orders=tuple(self._customer_order(order) for order in orders),
            previous_tickets=tuple(
                self._ticket_metadata(previous_ticket)
                for previous_ticket in previous_tickets
            ),
            previous_resolutions=tuple(
                self._previous_resolution(resolution)
                for resolution in previous_resolutions
            ),
        )

    async def _load_orders(self, customer_id: UUID) -> list[Order]:
        statement = (
            select(Order)
            .where(Order.customer_id == customer_id)
            .order_by(Order.order_date.desc())
            .limit(self._max_orders)
        )
        result = await self._session.scalars(statement)
        return list(result.all())

    async def _load_previous_tickets(
        self,
        customer_id: UUID,
        ticket_id: UUID,
    ) -> list[Ticket]:
        statement = (
            select(Ticket)
            .where(Ticket.customer_id == customer_id, Ticket.id != ticket_id)
            .order_by(Ticket.created_at.desc())
            .limit(self._max_previous_tickets)
        )
        result = await self._session.scalars(statement)
        return list(result.all())

    async def _load_previous_resolutions(
        self,
        customer_id: UUID,
        ticket_id: UUID,
    ) -> list[Resolution]:
        statement = (
            select(Resolution)
            .join(Ticket, Resolution.ticket_id == Ticket.id)
            .where(Ticket.customer_id == customer_id, Ticket.id != ticket_id)
            .order_by(Resolution.created_at.desc())
            .limit(self._max_previous_resolutions)
        )
        result = await self._session.scalars(statement)
        return list(result.all())

    @staticmethod
    def _customer_profile(customer: Customer) -> CustomerProfile:
        return CustomerProfile(
            id=customer.id,
            full_name=customer.full_name,
            email=customer.email,
            phone=customer.phone,
            tier=customer.tier,
            created_at=customer.created_at,
        )

    @staticmethod
    def _customer_account(account: Account) -> CustomerAccount:
        return CustomerAccount(
            id=account.id,
            customer_id=account.customer_id,
            plan_type=account.plan_type,
            status=account.status,
            signup_date=account.signup_date,
            billing_cycle=account.billing_cycle,
        )

    @staticmethod
    def _customer_order(order: Order) -> CustomerOrder:
        return CustomerOrder(
            id=order.id,
            customer_id=order.customer_id,
            product_name=order.product_name,
            amount=order.amount,
            currency=order.currency,
            status=order.status,
            order_date=order.order_date,
            delivery_eta=order.delivery_eta,
        )

    @staticmethod
    def _ticket_metadata(ticket: Ticket) -> TicketMetadata:
        return TicketMetadata(
            id=ticket.id,
            customer_id=ticket.customer_id,
            order_id=ticket.order_id,
            subject=ticket.subject,
            description=ticket.description,
            category=ticket.category,
            priority=ticket.priority,
            status=ticket.status,
            sentiment=ticket.sentiment,
            intent=ticket.intent,
            ai_summary=ticket.ai_summary,
            created_at=ticket.created_at,
            updated_at=ticket.updated_at,
        )

    @staticmethod
    def _previous_resolution(resolution: Resolution) -> PreviousResolution:
        return PreviousResolution(
            id=resolution.id,
            ticket_id=resolution.ticket_id,
            generated_response=resolution.generated_response,
            confidence_score=resolution.confidence_score,
            escalation_required=resolution.escalation_required,
            resolution_status=resolution.resolution_status,
            model_name=resolution.model_name,
            created_at=resolution.created_at,
        )

    @staticmethod
    def _validate_limit(name: str, value: int) -> None:
        if value < 1:
            raise ValueError(f"{name} must be greater than zero")
