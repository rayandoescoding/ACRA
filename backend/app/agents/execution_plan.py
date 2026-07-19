"""The typed, non-executing output of the planning layer."""

from dataclasses import dataclass

from app.agents.planning_models import NextAgent, PlanningAction, RequiredContext


@dataclass(frozen=True, slots=True)
class ExecutionPlan:
    """A recommendation for the next handling stage of a support ticket."""

    action: PlanningAction
    requires_human: bool
    confidence: float
    reason: str
    required_context: tuple[RequiredContext, ...]
    next_agent: NextAgent

    def __post_init__(self) -> None:
        if not 0.0 <= self.confidence <= 1.0:
            raise ValueError("confidence must be between 0.0 and 1.0")
        if not self.reason.strip():
            raise ValueError("reason must not be empty")
