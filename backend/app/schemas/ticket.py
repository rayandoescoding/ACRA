"""Pydantic schemas for support ticket resources."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.ticket import TicketPriority, TicketStatus


class TicketCreate(BaseModel):
    customer_id: UUID
    order_id: Optional[UUID] = None
    subject: str = Field(min_length=1, max_length=255)
    description: Optional[str] = None
    category: Optional[str] = Field(default=None, max_length=100)
    priority: TicketPriority = TicketPriority.MEDIUM
    status: TicketStatus = TicketStatus.OPEN


class TicketUpdate(BaseModel):
    order_id: Optional[UUID] = None
    subject: Optional[str] = Field(default=None, min_length=1, max_length=255)
    description: Optional[str] = None
    category: Optional[str] = Field(default=None, max_length=100)
    priority: Optional[TicketPriority] = None
    status: Optional[TicketStatus] = None
    sentiment: Optional[str] = Field(default=None, max_length=50)
    intent: Optional[str] = Field(default=None, max_length=100)
    ai_summary: Optional[str] = None


class TicketResponse(BaseModel):
    id: UUID
    customer_id: UUID
    order_id: Optional[UUID]
    subject: str
    description: Optional[str]
    category: Optional[str]
    priority: TicketPriority
    status: TicketStatus
    sentiment: Optional[str]
    intent: Optional[str]
    ai_summary: Optional[str]
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
