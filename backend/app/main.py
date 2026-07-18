import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.router import api_router as root_router
from app.api.v1.router import api_router as v1_router
from app.core.config import settings
from app.core.logging import setup_logging

# Setup standard application logging with JSON Formatter
setup_logging()
logger = logging.getLogger("acra_backend")


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    Context manager to handle application startup and shutdown lifecycle events
    with structured logging.
    """
    # Structured startup log
    logger.info(
        "Starting up ACRA Backend...",
        extra={
            "app_name": settings.APP_NAME,
            "app_version": settings.APP_VERSION,
            "environment": settings.ENVIRONMENT,
            "debug": settings.DEBUG,
            "host": settings.HOST,
            "port": settings.PORT,
        },
    )
    yield
    # Structured shutdown log
    logger.info(
        "Shutting down ACRA Backend...",
        extra={
            "app_name": settings.APP_NAME,
            "app_version": settings.APP_VERSION,
        },
    )


# Configure the FastAPI application metadata and endpoints
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Autonomous Multi-Agent Customer Resolution Platform (ACRA) Backend",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Configure CORS middleware with allowed origins from settings
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount API routers
app.include_router(v1_router, prefix="/api/v1")
app.include_router(root_router)


