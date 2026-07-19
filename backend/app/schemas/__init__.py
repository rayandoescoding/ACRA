"""
Pydantic schemas and serialization definitions package.
"""

from app.schemas.account import AccountCreate, AccountResponse, AccountUpdate
from app.schemas.customer import CustomerCreate, CustomerResponse, CustomerUpdate
from app.schemas.order import OrderCreate, OrderResponse, OrderUpdate
from app.schemas.resolution import ResolutionCreate, ResolutionResponse, ResolutionUpdate
from app.schemas.ticket import TicketCreate, TicketResponse, TicketUpdate
from app.schemas.auth import (
    AccessTokenResponse,
    AuthenticatedUserResponse,
    LoginRequest,
)
from app.schemas.ticket_processing import TicketProcessingResponse

__all__ = [
    "AccountCreate",
    "AccountResponse",
    "AccountUpdate",
    "AccessTokenResponse",
    "AuthenticatedUserResponse",
    "CustomerCreate",
    "CustomerResponse",
    "CustomerUpdate",
    "OrderCreate",
    "OrderResponse",
    "OrderUpdate",
    "LoginRequest",
    "ResolutionCreate",
    "ResolutionResponse",
    "ResolutionUpdate",
    "TicketCreate",
    "TicketResponse",
    "TicketProcessingResponse",
    "TicketUpdate",
]
