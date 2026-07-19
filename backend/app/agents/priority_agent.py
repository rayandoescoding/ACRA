"""Deterministic ticket-priority scoring independent of AI classification."""

from dataclasses import dataclass
from enum import Enum

from app.agents.base import AgentResult, BaseAgent
from app.agents.classification_agent import IntentLabel, SentimentLabel
from app.models.customer import CustomerTier
from app.models.ticket import TicketPriority


class SLAStatus(str, Enum):
    """Caller-supplied SLA signal used by deterministic priority scoring."""

    ON_TRACK = "on_track"
    AT_RISK = "at_risk"
    BREACHED = "breached"


class PriorityLevel(str, Enum):
    """Business-level priority outputs for Phase 4."""

    CRITICAL = "critical"
    HIGH = "high"
    STANDARD = "standard"


@dataclass(frozen=True, slots=True)
class PriorityInput:
    """Normalized inputs for deterministic ticket-priority scoring."""

    sentiment: SentimentLabel
    intent: IntentLabel
    customer_tier: CustomerTier
    sla_status: SLAStatus


@dataclass(frozen=True, slots=True)
class PriorityDecision:
    """Priority score and its mapping to the persisted ticket priority."""

    level: PriorityLevel
    score: int
    ticket_priority: TicketPriority


class PriorityAgent(BaseAgent[PriorityInput, PriorityDecision]):
    """Calculates priority with deterministic, inspectable business rules."""

    _INTENT_WEIGHTS = {
        IntentLabel.ACCOUNT_ACCESS: 2,
        IntentLabel.BILLING: 2,
        IntentLabel.CANCELLATION: 1,
        IntentLabel.DELIVERY: 1,
        IntentLabel.PRODUCT_ISSUE: 1,
        IntentLabel.REFUND: 2,
        IntentLabel.GENERAL_SUPPORT: 0,
    }
    _TIER_WEIGHTS = {
        CustomerTier.STANDARD: 0,
        CustomerTier.PREMIUM: 1,
        CustomerTier.VIP: 2,
    }
    _SLA_WEIGHTS = {
        SLAStatus.ON_TRACK: 0,
        SLAStatus.AT_RISK: 2,
        SLAStatus.BREACHED: 4,
    }

    async def execute(self, input_data: PriorityInput) -> AgentResult[PriorityDecision]:
        """Calculate a deterministic priority decision from normalized inputs."""
        score = self._score(input_data)
        if score >= 7:
            decision = PriorityDecision(
                level=PriorityLevel.CRITICAL,
                score=score,
                ticket_priority=TicketPriority.CRITICAL,
            )
        elif score >= 4:
            decision = PriorityDecision(
                level=PriorityLevel.HIGH,
                score=score,
                ticket_priority=TicketPriority.HIGH,
            )
        else:
            decision = PriorityDecision(
                level=PriorityLevel.STANDARD,
                score=score,
                ticket_priority=TicketPriority.MEDIUM,
            )
        return AgentResult(value=decision)

    def _score(self, priority_input: PriorityInput) -> int:
        """Score each supported input independently for clear policy auditing."""
        sentiment_weight = 2 if priority_input.sentiment is SentimentLabel.NEGATIVE else 0
        return (
            sentiment_weight
            + self._INTENT_WEIGHTS[priority_input.intent]
            + self._TIER_WEIGHTS[priority_input.customer_tier]
            + self._SLA_WEIGHTS[priority_input.sla_status]
        )
