"""
Pydantic schemas and serialization definitions package.
"""

from app.schemas.account import AccountCreate, AccountResponse, AccountUpdate
from app.schemas.customer import CustomerCreate, CustomerResponse, CustomerUpdate
from app.schemas.order import OrderCreate, OrderResponse, OrderUpdate
from app.schemas.resolution import ResolutionCreate, ResolutionResponse, ResolutionUpdate
from app.schemas.ticket import TicketCreate, TicketResponse, TicketUpdate

__all__ = [
    "AccountCreate",
    "AccountResponse",
    "AccountUpdate",
    "CustomerCreate",
    "CustomerResponse",
    "CustomerUpdate",
    "OrderCreate",
    "OrderResponse",
    "OrderUpdate",
    "ResolutionCreate",
    "ResolutionResponse",
    "ResolutionUpdate",
    "TicketCreate",
    "TicketResponse",
    "TicketUpdate",
]
