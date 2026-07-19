"""Phase 6 deterministic planning from a retrieved context package."""

from typing import Protocol

from app.agents.base import AgentResult, BaseAgent
from app.agents.context_models import ContextPackage
from app.agents.execution_plan import ExecutionPlan
from app.agents.planning_models import NextAgent, PlanningAction, RequiredContext
from app.models.ticket import TicketPriority


class PlanningStrategy(Protocol):
    """Replaceable async planning strategy for deterministic or LLM planners."""

    async def create_plan(self, context: ContextPackage) -> ExecutionPlan:
        """Recommend the next action for one complete context package."""
        ...


class DeterministicPlanningStrategy:
    """Rules-only planner that recommends handling without performing it."""

    async def create_plan(self, context: ContextPackage) -> ExecutionPlan:
        """Convert known ticket signals into a typed handling recommendation."""
        if context.priority is TicketPriority.CRITICAL:
            return ExecutionPlan(
                action=PlanningAction.ESCALATE,
                requires_human=True,
                confidence=0.95,
                reason="The ticket has critical priority and requires human review.",
                required_context=(
                    RequiredContext.TICKET,
                    RequiredContext.CUSTOMER_PROFILE,
                    RequiredContext.PREVIOUS_TICKETS,
                    RequiredContext.PREVIOUS_RESOLUTIONS,
                ),
                next_agent=NextAgent.HUMAN_REVIEW,
            )

        intent = (context.intent or "").strip().casefold()
        if intent == "refund":
            return ExecutionPlan(
                action=PlanningAction.REFUND,
                requires_human=False,
                confidence=0.85,
                reason="The ticket intent indicates a refund request.",
                required_context=(
                    RequiredContext.TICKET,
                    RequiredContext.CUSTOMER_PROFILE,
                    RequiredContext.CUSTOMER_ORDERS,
                ),
                next_agent=NextAgent.ORDER_OPERATIONS,
            )
        if intent == "cancellation":
            return ExecutionPlan(
                action=PlanningAction.CANCEL_ORDER,
                requires_human=False,
                confidence=0.85,
                reason="The ticket intent indicates an order or subscription cancellation request.",
                required_context=(
                    RequiredContext.TICKET,
                    RequiredContext.CUSTOMER_ACCOUNT,
                    RequiredContext.CUSTOMER_ORDERS,
                ),
                next_agent=NextAgent.ORDER_OPERATIONS,
            )
        if intent in {"account_access", "billing"}:
            return ExecutionPlan(
                action=PlanningAction.UPDATE_ACCOUNT,
                requires_human=False,
                confidence=0.75,
                reason="The ticket intent concerns account access or billing information.",
                required_context=(
                    RequiredContext.TICKET,
                    RequiredContext.CUSTOMER_PROFILE,
                    RequiredContext.CUSTOMER_ACCOUNT,
                ),
                next_agent=NextAgent.ACCOUNT_OPERATIONS,
            )
        if intent in {"delivery", "product_issue"}:
            return ExecutionPlan(
                action=PlanningAction.TROUBLESHOOT,
                requires_human=False,
                confidence=0.7,
                reason="The ticket intent indicates a delivery or product issue.",
                required_context=(
                    RequiredContext.TICKET,
                    RequiredContext.CUSTOMER_ORDERS,
                    RequiredContext.PREVIOUS_TICKETS,
                ),
                next_agent=NextAgent.RESOLUTION_GENERATION,
            )

        return ExecutionPlan(
            action=PlanningAction.ASK_FOR_INFORMATION,
            requires_human=False,
            confidence=0.55,
            reason="The available context does not identify a sufficiently specific handling action.",
            required_context=(
                RequiredContext.TICKET,
                RequiredContext.CUSTOMER_PROFILE,
            ),
            next_agent=NextAgent.INFORMATION_COLLECTION,
        )


class PlanningAgent(BaseAgent[ContextPackage, ExecutionPlan]):
    """Async facade for creating an execution plan from retrieved context."""

    def __init__(self, strategy: PlanningStrategy | None = None) -> None:
        self._strategy = strategy or DeterministicPlanningStrategy()

    async def execute(self, input_data: ContextPackage) -> AgentResult[ExecutionPlan]:
        """Produce a plan without enforcing, generating, or executing it."""
        plan = await self._strategy.create_plan(input_data)
        return AgentResult(value=plan)
