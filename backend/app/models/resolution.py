import enum
import uuid
from datetime import datetime
from typing import Optional, TYPE_CHECKING

from sqlalchemy import Boolean, DateTime, Enum, Float, ForeignKey, String, Text, UUID, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base

if TYPE_CHECKING:
    from app.models.ticket import Ticket


class ResolutionStatus(str, enum.Enum):
    """
    Enum representing the review/approval state of an AI-generated resolution.
    """
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class Resolution(Base):
    """
    Resolution database model representing an AI-generated response to a Ticket.

    A resolution stores the full text of the AI's proposed response, a
    confidence score reflecting how certain the model is, a flag indicating
    whether human escalation is required, and the name of the AI model that
    produced the response. Resolutions begin in PENDING status and are
    transitioned to APPROVED or REJECTED by the review workflow.
    """

    __tablename__ = "resolutions"

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
    )

    ticket_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("tickets.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )

    generated_response: Mapped[Optional[str]] = mapped_column(
        Text,
        nullable=True,
        comment="Full AI-generated response text proposed for the customer.",
    )

    confidence_score: Mapped[Optional[float]] = mapped_column(
        Float,
        nullable=True,
        comment="Model confidence in the generated response, range 0.0 – 1.0.",
    )

    escalation_required: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
        comment="True when the AI determines a human agent must handle the ticket.",
    )

    resolution_status: Mapped[ResolutionStatus] = mapped_column(
        Enum(
            ResolutionStatus,
            values_callable=lambda enum_cls: [item.value for item in enum_cls],
        ),
        default=ResolutionStatus.PENDING,
        nullable=False,
        comment="Approval state of the resolution in the review workflow.",
    )

    model_name: Mapped[Optional[str]] = mapped_column(
        String(150),
        nullable=True,
        comment="Identifier of the AI model that generated this resolution.",
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        default=datetime.utcnow,
        nullable=False,
    )

    ticket: Mapped["Ticket"] = relationship(
        "Ticket",
        back_populates="resolutions",
        foreign_keys=[ticket_id],
    )