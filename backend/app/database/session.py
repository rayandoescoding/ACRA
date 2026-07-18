from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from app.core.config import settings

# Create async database engine with production-friendly defaults
engine = create_async_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_recycle=3600,
    future=True,
)

# AsyncSession factory configured to not expire instances on commit
async_session_factory = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependency function to provide a database session per request.
    Yields AsyncSession and guarantees session cleanup on request completion.
    """
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()
