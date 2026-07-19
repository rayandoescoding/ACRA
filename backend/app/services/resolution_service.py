"""Business operations for AI-generated ticket resolutions."""

from uuid import UUID

from fastapi import Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.resolution import Resolution, ResolutionStatus
from app.schemas.resolution import ResolutionCreate, ResolutionResponse


class ResolutionNotFoundError(LookupError):
    """Raised when a requested ticket resolution does not exist."""

    def __init__(self, resolution_id: UUID) -> None:
        self.resolution_id = resolution_id
        super().__init__(f"Resolution '{resolution_id}' was not found.")


class ResolutionService:
    """Encapsulates persistence and review decisions for ticket resolutions."""

    def __init__(self, db: AsyncSession) -> None:
        self.db = db

    async def create_resolution(
        self,
        resolution_data: ResolutionCreate,
    ) -> ResolutionResponse:
        """Create and return a resolution proposal."""
        resolution = Resolution(**resolution_data.model_dump())
        self.db.add(resolution)
        await self.db.commit()
        await self.db.refresh(resolution)
        return ResolutionResponse.model_validate(resolution)

    async def get_resolution(self, resolution_id: UUID) -> ResolutionResponse:
        """Return a resolution by ID or raise ``ResolutionNotFoundError``."""
        resolution = await self._get_resolution_model(resolution_id)
        return ResolutionResponse.model_validate(resolution)

    async def list_resolutions(
        self,
        *,
        offset: int = 0,
        limit: int = 100,
    ) -> list[ResolutionResponse]:
        """Return resolution proposals in newest-first order with pagination."""
        if offset < 0:
            raise ValueError("offset must be greater than or equal to zero")
        if limit < 1:
            raise ValueError("limit must be greater than zero")

        statement = (
            select(Resolution)
            .order_by(Resolution.created_at.desc())
            .offset(offset)
            .limit(limit)
        )
        result = await self.db.execute(statement)
        resolutions = result.scalars().all()
        return [ResolutionResponse.model_validate(resolution) for resolution in resolutions]

    async def approve_resolution(self, resolution_id: UUID) -> ResolutionResponse:
        """Mark a resolution proposal as approved and return it."""
        return await self._set_resolution_status(
            resolution_id,
            ResolutionStatus.APPROVED,
        )

    async def reject_resolution(self, resolution_id: UUID) -> ResolutionResponse:
        """Mark a resolution proposal as rejected and return it."""
        return await self._set_resolution_status(
            resolution_id,
            ResolutionStatus.REJECTED,
        )

    async def _set_resolution_status(
        self,
        resolution_id: UUID,
        status: ResolutionStatus,
    ) -> ResolutionResponse:
        """Persist a review status change for an existing resolution."""
        resolution = await self._get_resolution_model(resolution_id)
        resolution.resolution_status = status
        await self.db.commit()
        await self.db.refresh(resolution)
        return ResolutionResponse.model_validate(resolution)

    async def _get_resolution_model(self, resolution_id: UUID) -> Resolution:
        """Load a resolution ORM object or raise a service-level not-found error."""
        resolution = await self.db.get(Resolution, resolution_id)
        if resolution is None:
            raise ResolutionNotFoundError(resolution_id)
        return resolution


async def get_resolution_service(
    db: AsyncSession = Depends(get_db),
) -> ResolutionService:
    """Provide a resolution service backed by the application's request session."""
    return ResolutionService(db)
