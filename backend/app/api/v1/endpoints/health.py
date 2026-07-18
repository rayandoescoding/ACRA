from fastapi import APIRouter
from app.core.config import settings

router = APIRouter()


@router.get("/health")
async def get_health() -> dict[str, str]:
    """
    Health check endpoint returning service status, name, and current version.
    """
    return {
        "status": "healthy",
        "service": "ACRA Backend",
        "version": settings.APP_VERSION,
    }
