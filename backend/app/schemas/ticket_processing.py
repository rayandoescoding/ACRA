"""API response contracts for completed ticket-processing runs."""

from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field

from app.agents.classification_agent import IntentLabel, SentimentLabel
from app.agents.guardrail_models import GuardrailRule
from app.agents.planning_models import PlanningAction
from app.agents.priority_agent import PriorityLevel
from app.agents.resolution_models import ResolutionOutcome
from app.models.ticket import TicketPriority


class ClassificationResultResponse(BaseModel):
    """Classification output returned by the completed pipeline."""

    sentiment: SentimentLabel
    sentiment_score: float
    sentiment_confidence: float
    intent: IntentLabel
    intent_confidence: float
    used_fallback: bool


class PriorityResultResponse(BaseModel):
    """Priority output returned by the completed pipeline."""

    level: PriorityLevel
    score: int
    ticket_priority: TicketPriority


class GuardrailRuleResponse(BaseModel):
    """One deterministic guardrail rule evaluation."""

    rule: GuardrailRule
    passed: bool
    reason: Optional[str]
    risk_points: int


class GuardrailResultResponse(BaseModel):
    """Aggregated guardrail result returned by the pipeline."""

    passed: bool
    risk_score: int
    failure_reason: Optional[str]
    requires_human: bool
    evaluated_rules: list[GuardrailRuleResponse]


class ResolutionOutcomeResponse(BaseModel):
    """Final resolution output and its persisted record identifier."""

    outcome: ResolutionOutcome
    message: str
    performed_action: Optional[PlanningAction]
    requires_follow_up: bool
    follow_up_reason: Optional[str]
    persisted_resolution_id: UUID


class TicketProcessingResponse(BaseModel):
    """Structured API result for one completed ticket-processing execution."""

    ticket_id: UUID
    correlation_id: Optional[str] = None
    classification: ClassificationResultResponse
    priority: PriorityResultResponse
    planning_action: PlanningAction
    planning_requires_human: bool
    confidence: float = Field(ge=0.0, le=1.0)
    guardrail: GuardrailResultResponse
    resolution: ResolutionOutcomeResponse
    requires_human: bool
