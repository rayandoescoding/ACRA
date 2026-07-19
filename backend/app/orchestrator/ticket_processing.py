"""Orchestration of the complete ticket-resolution agent pipeline."""

from dataclasses import dataclass, replace
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.base import AgentResult
from app.agents.classification_agent import (
    ClassificationAgent,
    IntentLabel,
    SentimentLabel,
    TicketClassification,
)
from app.agents.context_agent import ContextRetrievalAgent
from app.agents.context_models import ContextPackage
from app.agents.execution_plan import ExecutionPlan
from app.agents.guardrail_agent import GuardrailAgent
from app.agents.guardrail_models import GuardrailInput, GuardrailResult
from app.agents.planning_agent import PlanningAgent
from app.agents.priority_agent import (
    PriorityAgent,
    PriorityDecision,
    PriorityInput,
    SLAStatus,
)
from app.agents.resolution_agent import ResolutionAgent
from app.agents.resolution_models import ResolutionInput, ResolutionResult
from app.models.ticket import Ticket


class ProcessingTicketNotFoundError(LookupError):
    """Raised when processing is requested for a missing ticket."""

    def __init__(self, ticket_id: UUID) -> None:
        self.ticket_id = ticket_id
        super().__init__(f"Ticket '{ticket_id}' was not found for processing.")


@dataclass(frozen=True, slots=True)
class TicketProcessingResult:
    """Combined output from the ticket-resolution pipeline."""

    ticket_id: UUID
    classification: AgentResult[TicketClassification]
    priority: AgentResult[PriorityDecision]
    context: ContextPackage | None = None
    plan: AgentResult[ExecutionPlan] | None = None
    guardrail: AgentResult[GuardrailResult] | None = None
    resolution: AgentResult[ResolutionResult] | None = None


class TicketProcessingOrchestrator:
    """Coordinates the ordered agent pipeline within one async transaction."""

    def __init__(
        self,
        session: AsyncSession,
        classification_agent: ClassificationAgent | None = None,
        context_agent: ContextRetrievalAgent | None = None,
        priority_agent: PriorityAgent | None = None,
        planning_agent: PlanningAgent | None = None,
        guardrail_agent: GuardrailAgent | None = None,
        resolution_agent: ResolutionAgent | None = None,
    ) -> None:
        self._session = session
        self._classification_agent = classification_agent or ClassificationAgent()
        self._context_agent = context_agent or ContextRetrievalAgent(session)
        self._priority_agent = priority_agent or PriorityAgent()
        self._planning_agent = planning_agent or PlanningAgent()
        self._guardrail_agent = guardrail_agent or GuardrailAgent()
        self._resolution_agent = resolution_agent or ResolutionAgent()

    async def process_ticket(
        self,
        ticket_id: UUID,
        *,
        sla_status: SLAStatus = SLAStatus.ON_TRACK,
    ) -> TicketProcessingResult:
        """Run classification through resolution and commit supported ticket updates."""
        ticket = await self._session.get(Ticket, ticket_id)
        if ticket is None:
            raise ProcessingTicketNotFoundError(ticket_id)

        classification = await self._classification_agent.classify_and_store(
            self._session,
            ticket,
        )
        context = (await self._context_agent.execute(ticket.id)).value
        priority = await self._priority_agent.execute(
            PriorityInput(
                sentiment=self._sentiment_from_context(context),
                intent=self._intent_from_context(context),
                customer_tier=context.customer.tier,
                sla_status=sla_status,
            )
        )
        ticket.priority = priority.value.ticket_priority
        await self._session.flush()
        planning_context = replace(
            context,
            ticket=replace(context.ticket, priority=ticket.priority),
            priority=ticket.priority,
        )
        plan = await self._planning_agent.execute(planning_context)
        guardrail = await self._guardrail_agent.execute(
            GuardrailInput(plan=plan.value, context=planning_context)
        )
        resolution = await self._resolution_agent.execute(
            ResolutionInput(
                plan=plan.value,
                guardrail=guardrail.value,
                context=planning_context,
            )
        )

        await self._session.commit()
        await self._session.refresh(ticket)

        return TicketProcessingResult(
            ticket_id=ticket.id,
            classification=classification,
            priority=priority,
            context=planning_context,
            plan=plan,
            guardrail=guardrail,
            resolution=resolution,
        )

    @staticmethod
    def _sentiment_from_context(context: ContextPackage) -> SentimentLabel:
        """Convert the context-owned sentiment label for priority scoring."""
        return SentimentLabel(context.sentiment or SentimentLabel.NEUTRAL.value)

    @staticmethod
    def _intent_from_context(context: ContextPackage) -> IntentLabel:
        """Convert the context-owned intent label for priority scoring."""
        return IntentLabel(context.intent or IntentLabel.GENERAL_SUPPORT.value)
