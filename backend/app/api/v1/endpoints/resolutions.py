"""Version 1 endpoints for AI-generated ticket resolutions."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status as http_status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.schemas.resolution import ResolutionCreate, ResolutionResponse
from app.services.resolution_service import ResolutionNotFoundError, ResolutionService


router = APIRouter(prefix="/resolutions", tags=["resolutions"])


@router.post(
    "",
    response_model=ResolutionResponse,
    status_code=http_status.HTTP_201_CREATED,
    summary="Create a resolution proposal",
)
async def create_resolution(
    resolution_data: ResolutionCreate,
    db: AsyncSession = Depends(get_db),
) -> ResolutionResponse:
    """Create a resolution proposal through the resolution service."""
    return await ResolutionService(db).create_resolution(resolution_data)


@router.get(
    "",
    response_model=list[ResolutionResponse],
    status_code=http_status.HTTP_200_OK,
    summary="List resolution proposals",
)
async def list_resolutions(
    offset: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=1_000),
    db: AsyncSession = Depends(get_db),
) -> list[ResolutionResponse]:
    """List resolution proposals through the resolution service."""
    return await ResolutionService(db).list_resolutions(offset=offset, limit=limit)


@router.get(
    "/{resolution_id}",
    response_model=ResolutionResponse,
    status_code=http_status.HTTP_200_OK,
    summary="Get a resolution proposal",
)
async def get_resolution(
    resolution_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> ResolutionResponse:
    """Get a resolution proposal by ID through the resolution service."""
    try:
        return await ResolutionService(db).get_resolution(resolution_id)
    except ResolutionNotFoundError as exc:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.post(
    "/{resolution_id}/approve",
    response_model=ResolutionResponse,
    status_code=http_status.HTTP_200_OK,
    summary="Approve a resolution proposal",
)
async def approve_resolution(
    resolution_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> ResolutionResponse:
    """Approve a resolution proposal through the resolution service."""
    try:
        return await ResolutionService(db).approve_resolution(resolution_id)
    except ResolutionNotFoundError as exc:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc


@router.post(
    "/{resolution_id}/reject",
    response_model=ResolutionResponse,
    status_code=http_status.HTTP_200_OK,
    summary="Reject a resolution proposal",
)
async def reject_resolution(
    resolution_id: UUID,
    db: AsyncSession = Depends(get_db),
) -> ResolutionResponse:
    """Reject a resolution proposal through the resolution service."""
    try:
        return await ResolutionService(db).reject_resolution(resolution_id)
    except ResolutionNotFoundError as exc:
        raise HTTPException(
            status_code=http_status.HTTP_404_NOT_FOUND,
            detail=str(exc),
        ) from exc
