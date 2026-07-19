"""Asynchronous ticket-text classification with deterministic fallback."""

from dataclasses import dataclass
from enum import Enum
from typing import Protocol

from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.base import AgentResult, BaseAgent
from app.models.ticket import Ticket


class SentimentLabel(str, Enum):
    """Supported ticket sentiment labels."""

    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"


class IntentLabel(str, Enum):
    """Supported high-level ticket intents."""

    ACCOUNT_ACCESS = "account_access"
    BILLING = "billing"
    CANCELLATION = "cancellation"
    DELIVERY = "delivery"
    PRODUCT_ISSUE = "product_issue"
    REFUND = "refund"
    GENERAL_SUPPORT = "general_support"


@dataclass(frozen=True, slots=True)
class TicketClassification:
    """Structured output from ticket-text classification."""

    sentiment: SentimentLabel
    sentiment_score: float
    sentiment_confidence: float
    intent: IntentLabel
    intent_confidence: float

    def __post_init__(self) -> None:
        if not -1.0 <= self.sentiment_score <= 1.0:
            raise ValueError("sentiment_score must be between -1.0 and 1.0")
        if not 0.0 <= self.sentiment_confidence <= 1.0:
            raise ValueError("sentiment_confidence must be between 0.0 and 1.0")
        if not 0.0 <= self.intent_confidence <= 1.0:
            raise ValueError("intent_confidence must be between 0.0 and 1.0")


class AsyncClassificationClient(Protocol):
    """Protocol for an optional external asynchronous classification provider."""

    async def classify(self, ticket_text: str) -> TicketClassification:
        """Classify ticket text and return a validated structured result."""
        ...


class ClassificationAgent(BaseAgent[str, TicketClassification]):
    """Classifies ticket text and falls back safely when an AI provider fails."""

    _POSITIVE_TERMS = frozenset({"appreciate", "excellent", "good", "great", "thanks"})
    _NEGATIVE_TERMS = frozenset(
        {
            "angry",
            "broken",
            "complaint",
            "disappointed",
            "frustrated",
            "hate",
            "issue",
            "problem",
            "terrible",
            "urgent",
        }
    )
    _INTENT_TERMS: tuple[tuple[IntentLabel, frozenset[str]], ...] = (
        (IntentLabel.REFUND, frozenset({"chargeback", "refund", "return"})),
        (IntentLabel.CANCELLATION, frozenset({"cancel", "cancellation", "terminate"})),
        (IntentLabel.ACCOUNT_ACCESS, frozenset({"access", "login", "password", "sign in"})),
        (IntentLabel.BILLING, frozenset({"bill", "charge", "invoice", "payment", "subscription"})),
        (IntentLabel.DELIVERY, frozenset({"delivery", "late", "package", "shipment", "shipping"})),
        (IntentLabel.PRODUCT_ISSUE, frozenset({"defect", "malfunction", "not working", "quality"})),
    )

    def __init__(self, client: AsyncClassificationClient | None = None) -> None:
        self._client = client

    async def execute(self, input_data: str) -> AgentResult[TicketClassification]:
        """Classify ticket text with an optional AI provider and safe fallback."""
        ticket_text = input_data.strip()
        if self._client is None:
            return AgentResult(
                value=self._fallback_classification(ticket_text),
                used_fallback=True,
                fallback_reason="No asynchronous classification client is configured.",
            )

        try:
            classification = await self._client.classify(ticket_text)
            return AgentResult(value=classification)
        except Exception as exc:
            return AgentResult(
                value=self._fallback_classification(ticket_text),
                used_fallback=True,
                fallback_reason=f"Classification client failed: {type(exc).__name__}",
            )

    async def classify_and_store(
        self,
        session: AsyncSession,
        ticket: Ticket,
    ) -> AgentResult[TicketClassification]:
        """Classify a ticket and stage supported fields in the current unit of work."""
        ticket_text = self._ticket_text(ticket)
        result = await self.execute(ticket_text)
        ticket.sentiment = result.value.sentiment.value
        ticket.intent = result.value.intent.value
        await session.flush()
        return result

    @classmethod
    def _fallback_classification(cls, ticket_text: str) -> TicketClassification:
        """Provide deterministic classification when no AI result is available."""
        normalized_text = ticket_text.casefold()
        positive_matches = sum(term in normalized_text for term in cls._POSITIVE_TERMS)
        negative_matches = sum(term in normalized_text for term in cls._NEGATIVE_TERMS)
        evidence_count = positive_matches + negative_matches

        if negative_matches > positive_matches:
            sentiment = SentimentLabel.NEGATIVE
        elif positive_matches > negative_matches:
            sentiment = SentimentLabel.POSITIVE
        else:
            sentiment = SentimentLabel.NEUTRAL

        sentiment_score = 0.0
        if evidence_count:
            sentiment_score = round((positive_matches - negative_matches) / evidence_count, 2)
        sentiment_confidence = round(min(0.55 + evidence_count * 0.08, 0.85), 2)

        intent = IntentLabel.GENERAL_SUPPORT
        intent_matches = 0
        for candidate, terms in cls._INTENT_TERMS:
            candidate_matches = sum(term in normalized_text for term in terms)
            if candidate_matches > intent_matches:
                intent = candidate
                intent_matches = candidate_matches

        intent_confidence = round(min(0.5 + intent_matches * 0.15, 0.9), 2)
        return TicketClassification(
            sentiment=sentiment,
            sentiment_score=sentiment_score,
            sentiment_confidence=sentiment_confidence,
            intent=intent,
            intent_confidence=intent_confidence,
        )

    @staticmethod
    def _ticket_text(ticket: Ticket) -> str:
        """Build the text payload from the fields available on a ticket."""
        return "\n".join(part for part in (ticket.subject, ticket.description) if part)
