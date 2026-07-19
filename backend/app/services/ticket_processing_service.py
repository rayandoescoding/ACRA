"""Service integration for executing and persisting ticket-processing results."""

from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.orchestrator import (
    ProcessingTicketNotFoundError,
    TicketProcessingOrchestrator,
)
from app.schemas.resolution import ResolutionCreate
from app.schemas.ticket_processing import (
    ClassificationResultResponse,
    GuardrailResultResponse,
    GuardrailRuleResponse,
    PriorityResultResponse,
    ResolutionOutcomeResponse,
    TicketProcessingResponse,
)
from app.services.resolution_service import ResolutionService


class TicketProcessingNotFoundError(LookupError):
    """Raised when a requested ticket cannot be processed because it is missing."""

    def __init__(self, ticket_id: UUID) -> None:
        self.ticket_id = ticket_id
        super().__init__(f"Ticket '{ticket_id}' was not found for processing.")


class TicketProcessingService:
    """Runs the existing orchestrator and persists its final resolution only."""

    _MODEL_NAME = "acra_ticket_processing_pipeline"

    def __init__(
        self,
        db: AsyncSession,
        orchestrator: TicketProcessingOrchestrator | None = None,
    ) -> None:
        self._db = db
        self._orchestrator = orchestrator or TicketProcessingOrchestrator(db)

    async def process_ticket(self, ticket_id: UUID) -> TicketProcessingResponse:
        """Execute the pipeline once and save its final customer resolution."""
        try:
            pipeline_result = await self._orchestrator.process_ticket(ticket_id)
        except ProcessingTicketNotFoundError as exc:
            raise TicketProcessingNotFoundError(ticket_id) from exc

        plan = pipeline_result.plan.value
        guardrail = pipeline_result.guardrail.value
        resolution = pipeline_result.resolution.value
        persisted_resolution = await ResolutionService(self._db).create_resolution(
            ResolutionCreate(
                ticket_id=pipeline_result.ticket_id,
                generated_response=resolution.message,
                confidence_score=plan.confidence,
                escalation_required=guardrail.requires_human,
                model_name=self._MODEL_NAME,
            )
        )

        return TicketProcessingResponse(
            ticket_id=pipeline_result.ticket_id,
            classification=ClassificationResultResponse(
                sentiment=pipeline_result.classification.value.sentiment,
                sentiment_score=pipeline_result.classification.value.sentiment_score,
                sentiment_confidence=(
                    pipeline_result.classification.value.sentiment_confidence
                ),
                intent=pipeline_result.classification.value.intent,
                intent_confidence=(
                    pipeline_result.classification.value.intent_confidence
                ),
                used_fallback=pipeline_result.classification.used_fallback,
            ),
            priority=PriorityResultResponse(
                level=pipeline_result.priority.value.level,
                score=pipeline_result.priority.value.score,
                ticket_priority=pipeline_result.priority.value.ticket_priority,
            ),
            planning_action=plan.action,
            planning_requires_human=plan.requires_human,
            confidence=plan.confidence,
            guardrail=GuardrailResultResponse(
                passed=guardrail.passed,
                risk_score=guardrail.risk_score,
                failure_reason=guardrail.failure_reason,
                requires_human=guardrail.requires_human,
                evaluated_rules=[
                    GuardrailRuleResponse(
                        rule=evaluation.rule,
                        passed=evaluation.passed,
                        reason=evaluation.reason,
                        risk_points=evaluation.risk_points,
                    )
                    for evaluation in guardrail.evaluated_rules
                ],
            ),
            resolution=ResolutionOutcomeResponse(
                outcome=resolution.outcome,
                message=resolution.message,
                performed_action=resolution.performed_action,
                requires_follow_up=resolution.requires_follow_up,
                follow_up_reason=resolution.follow_up_reason,
                persisted_resolution_id=persisted_resolution.id,
            ),
            requires_human=guardrail.requires_human,
        )
