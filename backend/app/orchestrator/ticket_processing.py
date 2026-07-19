"""Orchestration of the complete ticket-resolution agent pipeline."""

from dataclasses import dataclass, replace
from time import perf_counter
from typing import Awaitable, Callable, TypeVar
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
from app.observability.logger import PipelineEventLogger, pipeline_logger
from app.observability.metrics import PipelineMetrics, pipeline_metrics
from app.observability.tracing import pipeline_trace


ResultT = TypeVar("ResultT")


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
        metrics: PipelineMetrics | None = None,
        event_logger: PipelineEventLogger | None = None,
    ) -> None:
        self._session = session
        self._classification_agent = classification_agent or ClassificationAgent()
        self._context_agent = context_agent or ContextRetrievalAgent(session)
        self._priority_agent = priority_agent or PriorityAgent()
        self._planning_agent = planning_agent or PlanningAgent()
        self._guardrail_agent = guardrail_agent or GuardrailAgent()
        self._resolution_agent = resolution_agent or ResolutionAgent()
        self._metrics = metrics or pipeline_metrics
        self._event_logger = event_logger or pipeline_logger

    async def process_ticket(
        self,
        ticket_id: UUID,
        *,
        sla_status: SLAStatus = SLAStatus.ON_TRACK,
    ) -> TicketProcessingResult:
        """Run classification through resolution and commit supported ticket updates."""
        async with pipeline_trace() as trace:
            self._event_logger.info(
                "pipeline_started",
                correlation_id=trace.correlation_id,
            )
            try:
                ticket = await self._session.get(Ticket, ticket_id)
                if ticket is None:
                    raise ProcessingTicketNotFoundError(ticket_id)

                classification = await self._observe_agent(
                    "classification",
                    lambda: self._classification_agent.classify_and_store(
                        self._session,
                        ticket,
                    ),
                )
                self._event_logger.info(
                    "classification_completed",
                    correlation_id=trace.correlation_id,
                    sentiment=classification.value.sentiment.value,
                    intent=classification.value.intent.value,
                    used_fallback=classification.used_fallback,
                )
                context = (
                    await self._observe_agent(
                        "context_retrieval",
                        lambda: self._context_agent.execute(ticket.id),
                    )
                ).value
                priority = await self._observe_agent(
                    "priority",
                    lambda: self._priority_agent.execute(
                        PriorityInput(
                            sentiment=self._sentiment_from_context(context),
                            intent=self._intent_from_context(context),
                            customer_tier=context.customer.tier,
                            sla_status=sla_status,
                        )
                    ),
                )
                self._event_logger.info(
                    "priority_completed",
                    correlation_id=trace.correlation_id,
                    priority_level=priority.value.level.value,
                    priority_score=priority.value.score,
                )
                ticket.priority = priority.value.ticket_priority
                await self._session.flush()
                planning_context = replace(
                    context,
                    ticket=replace(context.ticket, priority=ticket.priority),
                    priority=ticket.priority,
                )
                plan = await self._observe_agent(
                    "planning",
                    lambda: self._planning_agent.execute(planning_context),
                )
                self._event_logger.info(
                    "planning_completed",
                    correlation_id=trace.correlation_id,
                    planning_action=plan.value.action.value,
                    requires_human=plan.value.requires_human,
                )
                guardrail = await self._observe_agent(
                    "guardrails",
                    lambda: self._guardrail_agent.execute(
                        GuardrailInput(plan=plan.value, context=planning_context)
                    ),
                )
                self._event_logger.info(
                    "guardrails_completed",
                    correlation_id=trace.correlation_id,
                    outcome="passed" if guardrail.value.passed else "failed",
                    requires_human=guardrail.value.requires_human,
                    risk_score=guardrail.value.risk_score,
                )
                resolution = await self._observe_agent(
                    "resolution",
                    lambda: self._resolution_agent.execute(
                        ResolutionInput(
                            plan=plan.value,
                            guardrail=guardrail.value,
                            context=planning_context,
                        )
                    ),
                )
                self._event_logger.info(
                    "resolution_completed",
                    correlation_id=trace.correlation_id,
                    outcome=resolution.value.outcome.value,
                    requires_human=guardrail.value.requires_human,
                )

                await self._session.commit()
                await self._session.refresh(ticket)
            except Exception as exc:
                await self._metrics.record_pipeline_completion(
                    succeeded=False,
                    requires_human=False,
                )
                self._event_logger.info(
                    "pipeline_failed",
                    correlation_id=trace.correlation_id,
                    outcome=type(exc).__name__,
                    succeeded=False,
                )
                raise

            await self._metrics.record_pipeline_completion(
                succeeded=True,
                requires_human=guardrail.value.requires_human,
            )
            self._event_logger.info(
                "pipeline_completed",
                correlation_id=trace.correlation_id,
                duration_ms=round(trace.elapsed_ms(), 2),
                succeeded=True,
                requires_human=guardrail.value.requires_human,
            )
            return TicketProcessingResult(
                ticket_id=ticket.id,
                classification=classification,
                priority=priority,
                context=planning_context,
                plan=plan,
                guardrail=guardrail,
                resolution=resolution,
            )

    async def _observe_agent(
        self,
        agent: str,
        operation: Callable[[], Awaitable[ResultT]],
    ) -> ResultT:
        """Time an agent invocation while preserving its result or exception."""
        started_at = perf_counter()
        try:
            result = await operation()
        except Exception:
            await self._metrics.record_agent_execution(
                agent,
                duration_ms=(perf_counter() - started_at) * 1_000,
                succeeded=False,
            )
            raise
        await self._metrics.record_agent_execution(
            agent,
            duration_ms=(perf_counter() - started_at) * 1_000,
            succeeded=True,
        )
        return result

    @staticmethod
    def _sentiment_from_context(context: ContextPackage) -> SentimentLabel:
        """Convert the context-owned sentiment label for priority scoring."""
        return SentimentLabel(context.sentiment or SentimentLabel.NEUTRAL.value)

    @staticmethod
    def _intent_from_context(context: ContextPackage) -> IntentLabel:
        """Convert the context-owned intent label for priority scoring."""
        return IntentLabel(context.intent or IntentLabel.GENERAL_SUPPORT.value)
