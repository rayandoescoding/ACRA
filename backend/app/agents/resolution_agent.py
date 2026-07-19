"""Asynchronous deterministic resolution generation from an approved plan."""

from app.agents.base import AgentResult, BaseAgent
from app.agents.context_models import ContextPackage
from app.agents.execution_plan import ExecutionPlan
from app.agents.guardrail_models import GuardrailResult
from app.agents.planning_models import PlanningAction
from app.agents.resolution_models import (
    ResolutionInput,
    ResolutionOutcome,
    ResolutionResult,
)


class ResolutionAgent(BaseAgent[ResolutionInput, ResolutionResult]):
    """Produces deterministic resolution messages without executing external actions."""

    async def execute(self, input_data: ResolutionInput) -> AgentResult[ResolutionResult]:
        """Produce a resolution result from an already approved execution plan."""
        result = await self.resolve(
            input_data.plan,
            input_data.guardrail,
            input_data.context,
        )
        return AgentResult(value=result)

    async def resolve(
        self,
        plan: ExecutionPlan,
        guardrail: GuardrailResult,
        context: ContextPackage,
    ) -> ResolutionResult:
        """Generate a deterministic response without changing the planned action."""
        if guardrail.requires_human:
            return self._human_review_result(plan, guardrail, context)

        return self._automated_result(plan, guardrail, context)

    @staticmethod
    def _human_review_result(
        plan: ExecutionPlan,
        guardrail: GuardrailResult,
        context: ContextPackage,
    ) -> ResolutionResult:
        """Return a non-automated outcome whenever human review is required."""
        reason = guardrail.failure_reason or plan.reason
        return ResolutionResult(
            outcome=ResolutionOutcome.HUMAN_REVIEW,
            message="Your request requires review by a support specialist before any action is taken.",
            performed_action=None,
            requires_follow_up=True,
            follow_up_reason=reason,
            metadata=ResolutionAgent._metadata(plan, guardrail, context),
        )

    @staticmethod
    def _automated_result(
        plan: ExecutionPlan,
        guardrail: GuardrailResult,
        context: ContextPackage,
    ) -> ResolutionResult:
        """Map the trusted planning action to its deterministic customer response."""
        metadata = ResolutionAgent._metadata(plan, guardrail, context)

        if plan.action is PlanningAction.REFUND:
            return ResolutionResult(
                outcome=ResolutionOutcome.AUTOMATED_RESPONSE,
                message="Your refund request has been approved for processing.",
                performed_action=plan.action,
                requires_follow_up=True,
                follow_up_reason="Confirm that the refund is completed.",
                metadata=metadata,
            )
        if plan.action is PlanningAction.CANCEL_ORDER:
            return ResolutionResult(
                outcome=ResolutionOutcome.AUTOMATED_RESPONSE,
                message="Your cancellation request has been accepted for processing.",
                performed_action=plan.action,
                requires_follow_up=True,
                follow_up_reason="Confirm that the cancellation is completed.",
                metadata=metadata,
            )
        if plan.action is PlanningAction.UPDATE_ACCOUNT:
            return ResolutionResult(
                outcome=ResolutionOutcome.AUTOMATED_RESPONSE,
                message="We have prepared the next account-support action for your request.",
                performed_action=plan.action,
                requires_follow_up=True,
                follow_up_reason="Confirm that the account request is completed.",
                metadata=metadata,
            )
        if plan.action is PlanningAction.TROUBLESHOOT:
            return ResolutionResult(
                outcome=ResolutionOutcome.AUTOMATED_RESPONSE,
                message="We have identified troubleshooting steps based on your ticket details.",
                performed_action=plan.action,
                requires_follow_up=True,
                follow_up_reason="Confirm whether the troubleshooting steps resolved the issue.",
                metadata=metadata,
            )
        if plan.action is PlanningAction.ASK_FOR_INFORMATION:
            return ResolutionResult(
                outcome=ResolutionOutcome.INFORMATION_REQUESTED,
                message="Please provide the additional information needed to continue with your request.",
                performed_action=plan.action,
                requires_follow_up=True,
                follow_up_reason="Await the customer's requested information.",
                metadata=metadata,
            )

        return ResolutionResult(
            outcome=ResolutionOutcome.HUMAN_REVIEW,
            message="Your request has been escalated to a support specialist for review.",
            performed_action=None,
            requires_follow_up=True,
            follow_up_reason=plan.reason,
            metadata=metadata,
        )

    @staticmethod
    def _metadata(
        plan: ExecutionPlan,
        guardrail: GuardrailResult,
        context: ContextPackage,
    ) -> dict[str, str]:
        """Build stable metadata without leaking ORM objects to later stages."""
        return {
            "ticket_id": str(context.ticket.id),
            "planned_action": plan.action.value,
            "guardrail_passed": str(guardrail.passed).lower(),
            "guardrail_risk_score": str(guardrail.risk_score),
        }
