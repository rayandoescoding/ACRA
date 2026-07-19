"""Business operations for support tickets."""

from uuid import UUID

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.ticket import Ticket, TicketStatus
from app.schemas.ticket import TicketCreate, TicketResponse


class TicketNotFoundError(LookupError):
    """Raised when a requested support ticket does not exist."""

    def __init__(self, ticket_id: UUID) -> None:
        self.ticket_id = ticket_id
        super().__init__(f"Ticket '{ticket_id}' was not found.")


class TicketService:
    """Encapsulates ticket persistence and ticket-specific business operations."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create_ticket(self, ticket_data: TicketCreate) -> TicketResponse:
        """Create and return a new support ticket."""
        ticket = Ticket(**ticket_data.model_dump())
        self.db.add(ticket)
        await self.db.commit()
        await self.db.refresh(ticket)
        return TicketResponse.model_validate(ticket)

    async def get_ticket(self, ticket_id: UUID) -> TicketResponse:
        """Return a ticket by ID or raise ``TicketNotFoundError``."""
        ticket = await self._get_ticket_model(ticket_id)
        return TicketResponse.model_validate(ticket)

    async def list_tickets(
        self,
        *,
        offset: int = 0,
        limit: int = 100,
    ) -> list[TicketResponse]:
        """Return tickets in newest-first order using offset pagination."""
        if offset < 0:
            raise ValueError("offset must be greater than or equal to zero")
        if limit < 1:
            raise ValueError("limit must be greater than zero")

        statement = (
            select(Ticket)
            .order_by(Ticket.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.db.execute(statement)
        tickets = result.scalars().all()
        return [TicketResponse.model_validate(ticket) for ticket in tickets]

    async def update_ticket_status(
        self,
        ticket_id: UUID,
        status: TicketStatus,
    ) -> TicketResponse:
        """Update a ticket's lifecycle status and return the updated ticket."""
        ticket = await self._get_ticket_model(ticket_id)
        ticket.status = status
        await self.db.commit()
        await self.db.refresh(ticket)
        return TicketResponse.model_validate(ticket)

    async def _get_ticket_model(self, ticket_id: UUID) -> Ticket:
        """Load a ticket ORM object or raise a service-level not-found error."""
        ticket = await self.db.get(Ticket, ticket_id)
        if ticket is None:
            raise TicketNotFoundError(ticket_id)
        return ticket


async def get_ticket_service(
    db: AsyncSession = Depends(get_db),
) -> TicketService:
    """Provide a ticket service backed by the application's request session."""
    return TicketService(db)
