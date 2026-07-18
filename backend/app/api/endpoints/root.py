from fastapi import APIRouter
from app.core.config import settings

router = APIRouter()


@router.get("/")
async def read_root() -> dict[str, str]:
    """
    Root API endpoint returning basic project status.
    """
    return {
        "project": settings.APP_NAME,
        "status": "running",
    }
