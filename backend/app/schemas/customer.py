"""Pydantic schemas for customer resources."""

from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.customer import CustomerTier


class CustomerCreate(BaseModel):
    full_name: str = Field(min_length=1, max_length=255)
    email: str = Field(min_length=1, max_length=255)
    phone: Optional[str] = Field(default=None, max_length=50)
    tier: CustomerTier = CustomerTier.STANDARD


class CustomerUpdate(BaseModel):
    full_name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    email: Optional[str] = Field(default=None, min_length=1, max_length=255)
    phone: Optional[str] = Field(default=None, max_length=50)
    tier: Optional[CustomerTier] = None


class CustomerResponse(BaseModel):
    id: UUID
    full_name: str
    email: str
    phone: Optional[str]
    tier: CustomerTier
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
