"""Version 1 endpoints for support tickets."""

from uuid import UUID

from fastapi import APIRouter, Body, Depends, HTTPException, Query, status as http_status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.ticket import TicketStatus
from app.schemas.ticket import TicketCreate, TicketResponse
from app.services.ticket_service import TicketNotFoundError, TicketService


router = APIRouter(prefix="/tickets", tags=["tickets"])


@router.post(
    "",
    response_model=TicketResponse,
    status_code=http_status.HTTP_201_CREATED,
    summary="Create a support ticket",
)
async def create_ticket(
    ticket_data: TicketCreate,
    db: AsyncSession = Depends(get_db),
) -> TicketResponse:
    """Create a support ticket through the ticket service."""
    return await TicketService(db).create_ticket(ticket_data)


@router.get(
    "",
    response_model=list[TicketResponse],
    status_code=http_status.HTTP_200_OK,
    summary="List support tickets",
)
async def list_tickets(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=1_000),
    db: AsyncSession = Depends(get_db),
) -> list[TicketResponse]:
    """List support tickets through the ticket service."""
    return await TicketService(db).list_tickets(offset=offset, limit=limit)


@router.get(
    "/{ticket_id}",
    response_model=TicketResponse,
    status_code=http_status.HTTP_200_OK,
    summary="Get a support ticket",
)
async def get_ticket(
    ticket_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> TicketResponse:
    """Get a support ticket by ID through the ticket service."""
    try:
        return await TicketService(db).get_ticket(ticket_id)
    except TicketNotFoundError as exc:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.patch(
    "/{ticket_id}/status",
    response_model=TicketResponse,
    status_code=http_status.HTTP_200_OK,
    summary="Update a ticket status",
)
async def update_ticket_status(
    ticket_id: UUID,
    status: TicketStatus = Body(embed=True),
    db: AsyncSession = Depends(get_db),
) -> TicketResponse:
    """Update a ticket lifecycle status through the ticket service."""
    try:
        return await TicketService(db).update_ticket_status(ticket_id, status)
    except TicketNotFoundError as exc:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
