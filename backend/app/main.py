from contextlib import asynccontextmanager
from typing import AsyncGenerator, Dict

from fastapi import FastAPI

from app.core.config import settings
from app.core.logging import setup_logging

# Setup standard application logging
setup_logging()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Context manager to handle application startup and shutdown lifecycle events.
    """
    # Startup tasks go here (e.g. database connection initialization)
    yield
    # Shutdown tasks go here (e.g. closing database connections)


app = FastAPI(
    title=settings.PROJECT_NAME,
    lifespan=lifespan,
)


@app.get("/")
async def read_root() -> Dict[str, str]:
    """
    Status / Healthcheck endpoint.
    """
    return {
        "project": settings.PROJECT_NAME,
        "status": "running",
    }

