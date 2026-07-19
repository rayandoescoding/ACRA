"""Typed inputs and outputs for deterministic guardrail evaluation."""

from dataclasses import dataclass
from enum import Enum

from app.agents.context_models import ContextPackage
from app.agents.execution_plan import ExecutionPlan


class GuardrailRule(str, Enum):
    """Deterministic rules evaluated before a plan reaches execution."""

    REQUIRED_CONTEXT = "required_context"
    REFUND_APPROVAL_LIMIT = "refund_approval_limit"
    REFUND_ELIGIBILITY_WINDOW = "refund_eligibility_window"
    ACCOUNT_FLAGGED = "account_flagged"
    EXCESSIVE_RECENT_REFUNDS = "excessive_recent_refunds"
    HIGH_RISK_CUSTOMER_STATE = "high_risk_customer_state"


@dataclass(frozen=True, slots=True)
class GuardrailInput:
    """The plan and retrieved context evaluated by the guardrail layer."""

    plan: ExecutionPlan
    context: ContextPackage


@dataclass(frozen=True, slots=True)
class RuleEvaluation:
    """Immutable outcome from one deterministic business-policy rule."""

    rule: GuardrailRule
    passed: bool
    reason: str | None
    risk_points: int

    def __post_init__(self) -> None:
        if self.risk_points < 0:
            raise ValueError("risk_points must be greater than or equal to zero")
        if not self.passed and not self.reason:
            raise ValueError("a failed rule must include a reason")


@dataclass(frozen=True, slots=True)
class GuardrailResult:
    """Decision produced before a future execution stage may act on a plan."""

    passed: bool
    risk_score: int
    failure_reason: str | None
    requires_human: bool
    evaluated_rules: tuple[RuleEvaluation, ...]

    def __post_init__(self) -> None:
        if not 0 <= self.risk_score <= 100:
            raise ValueError("risk_score must be between 0 and 100")
        has_failure = any(not evaluation.passed for evaluation in self.evaluated_rules)
        if has_failure and self.passed:
            raise ValueError("a result with failed rules cannot pass")
        if has_failure and not self.requires_human:
            raise ValueError("failed guardrail rules must require human involvement")
        if not self.passed and not self.failure_reason:
            raise ValueError("a failed result must include a failure reason")
