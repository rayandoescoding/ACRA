"""Phase 4 ticket-processing workflow for classification and priority."""

from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.base import AgentResult
from app.agents.classification_agent import ClassificationAgent, TicketClassification
from app.agents.priority_agent import (
    PriorityAgent,
    PriorityDecision,
    PriorityInput,
    SLAStatus,
)
from app.models.customer import Customer, CustomerTier
from app.models.ticket import Ticket


class ProcessingTicketNotFoundError(LookupError):
    """Raised when Phase 4 processing is requested for a missing ticket."""

    def __init__(self, ticket_id: UUID) -> None:
        self.ticket_id = ticket_id
        super().__init__(f"Ticket '{ticket_id}' was not found for processing.")


@dataclass(frozen=True, slots=True)
class TicketProcessingResult:
    """Combined output from classification and deterministic priority scoring."""

    ticket_id: UUID
    classification: AgentResult[TicketClassification]
    priority: AgentResult[PriorityDecision]


class TicketProcessingWorkflow:
    """Runs the bounded Phase 4 ticket-classification processing sequence."""

    def __init__(
        self,
        session: AsyncSession,
        classification_agent: ClassificationAgent | None = None,
        priority_agent: PriorityAgent | None = None,
    ) -> None:
        self._session = session
        self._classification_agent = classification_agent or ClassificationAgent()
        self._priority_agent = priority_agent or PriorityAgent()

    async def process_ticket(
        self,
        ticket_id: UUID,
        *,
        sla_status: SLAStatus = SLAStatus.ON_TRACK,
    ) -> TicketProcessingResult:
        """Classify and prioritize a ticket, then atomically persist supported fields."""
        ticket = await self._session.get(Ticket, ticket_id)
        if ticket is None:
            raise ProcessingTicketNotFoundError(ticket_id)

        classification = await self._classification_agent.classify_and_store(
            self._session,
            ticket,
        )
        customer_tier = await self._get_customer_tier(ticket.customer_id)
        priority = await self._priority_agent.execute(
            PriorityInput(
                sentiment=classification.value.sentiment,
                intent=classification.value.intent,
                customer_tier=customer_tier,
                sla_status=sla_status,
            )
        )
        ticket.priority = priority.value.ticket_priority

        await self._session.commit()
        await self._session.refresh(ticket)

        return TicketProcessingResult(
            ticket_id=ticket.id,
            classification=classification,
            priority=priority,
        )

    async def _get_customer_tier(self, customer_id: UUID) -> CustomerTier:
        """Read the customer tier without lazy-loading ORM relationships."""
        statement = select(Customer.tier).where(Customer.id == customer_id)
        customer_tier = await self._session.scalar(statement)
        if customer_tier is None:
            raise LookupError(f"Customer '{customer_id}' was not found for ticket processing.")
        return customer_tier
