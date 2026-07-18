"""Pydantic schemas for account resources."""

from datetime import date
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.account import AccountStatus


class AccountCreate(BaseModel):
    customer_id: UUID
    plan_type: str = Field(min_length=1, max_length=100)
    status: AccountStatus = AccountStatus.ACTIVE
    signup_date: date
    billing_cycle: str = Field(min_length=1, max_length=50)


class AccountUpdate(BaseModel):
    plan_type: Optional[str] = Field(default=None, min_length=1, max_length=100)
    status: Optional[AccountStatus] = None
    signup_date: Optional[date] = None
    billing_cycle: Optional[str] = Field(default=None, min_length=1, max_length=50)


class AccountResponse(BaseModel):
    id: UUID
    customer_id: UUID
    plan_type: str
    status: AccountStatus
    signup_date: date
    billing_cycle: str

    model_config = ConfigDict(from_attributes=True)
