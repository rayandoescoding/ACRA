"""Pydantic schemas for order resources."""

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from app.models.order import OrderStatus


class OrderCreate(BaseModel):
    customer_id: UUID
    product_name: str = Field(min_length=1, max_length=255)
    amount: Decimal
    currency: str = Field(default="USD", min_length=1, max_length=10)
    status: OrderStatus = OrderStatus.PLACED
    delivery_eta: Optional[datetime] = None


class OrderUpdate(BaseModel):
    product_name: Optional[str] = Field(default=None, min_length=1, max_length=255)
    amount: Optional[Decimal] = None
    currency: Optional[str] = Field(default=None, min_length=1, max_length=10)
    status: Optional[OrderStatus] = None
    delivery_eta: Optional[datetime] = None


class OrderResponse(BaseModel):
    id: UUID
    customer_id: UUID
    product_name: str
    amount: Decimal
    currency: str
    status: OrderStatus
    order_date: datetime
    delivery_eta: Optional[datetime]

    model_config = ConfigDict(from_attributes=True)
