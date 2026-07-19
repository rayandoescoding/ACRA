"""Typed contracts for deterministic resolution generation."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Mapping, Optional

from app.agents.context_models import ContextPackage
from app.agents.execution_plan import ExecutionPlan
from app.agents.guardrail_models import GuardrailResult
from app.agents.planning_models import PlanningAction


class ResolutionOutcome(str, Enum):
    """Possible outcomes from the resolution stage."""

    AUTOMATED_RESPONSE = "automated_response"
    HUMAN_REVIEW = "human_review"
    INFORMATION_REQUESTED = "information_requested"


@dataclass(frozen=True, slots=True)
class ResolutionInput:
    """Approved planning inputs consumed by the Resolution Agent."""

    plan: ExecutionPlan
    guardrail: GuardrailResult
    context: ContextPackage


@dataclass(frozen=True, slots=True)
class ResolutionResult:
    """Deterministic response prepared from an approved execution plan."""

    outcome: ResolutionOutcome
    message: str
    performed_action: Optional[PlanningAction]
    requires_follow_up: bool
    follow_up_reason: Optional[str]
    metadata: Mapping[str, str] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.message.strip():
            raise ValueError("message must not be empty")
        if self.requires_follow_up and not self.follow_up_reason:
            raise ValueError("follow_up_reason is required when follow-up is needed")
        if not self.requires_follow_up and self.follow_up_reason is not None:
            raise ValueError("follow_up_reason must be absent when no follow-up is needed")
