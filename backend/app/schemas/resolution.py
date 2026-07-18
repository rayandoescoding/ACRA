"""Pydantic schemas for AI-generated resolution resources."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.resolution import ResolutionStatus


class ResolutionCreate(BaseModel):
    ticket_id: UUID
    generated_response: Optional[str] = None
    confidence_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    escalation_required: bool = False
    resolution_status: ResolutionStatus = ResolutionStatus.PENDING
    model_name: Optional[str] = Field(default=None, max_length=150)


class ResolutionUpdate(BaseModel):
    generated_response: Optional[str] = None
    confidence_score: Optional[float] = Field(default=None, ge=0.0, le=1.0)
    escalation_required: Optional[bool] = None
    resolution_status: Optional[ResolutionStatus] = None
    model_name: Optional[str] = Field(default=None, max_length=150)


class ResolutionResponse(BaseModel):
    id: UUID
    ticket_id: UUID
    generated_response: Optional[str]
    confidence_score: Optional[float]
    escalation_required: bool
    resolution_status: ResolutionStatus
    model_name: Optional[str]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
