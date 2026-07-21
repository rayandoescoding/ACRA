"""Shared fixtures for isolated ACRA backend integration tests."""

import os
from collections.abc import AsyncGenerator
from uuid import UUID

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

test_database_url = os.getenv("ACRA_TEST_DATABASE_URL")
if not test_database_url:
    raise RuntimeError(
        "ACRA_TEST_DATABASE_URL must point to a dedicated disposable PostgreSQL database."
    )

os.environ["DATABASE_URL"] = test_database_url
os.environ["DEMO_SEED_ENABLED"] = "false"
os.environ["AUTH_BOOTSTRAP_ADMIN_EMAIL"] = ""
os.environ["AUTH_BOOTSTRAP_ADMIN_PASSWORD"] = ""

import app.models  # noqa: E402,F401
from app.api.dependencies.auth import get_current_user  # noqa: E402
from app.core.security import create_access_token, hash_password  # noqa: E402
from app.database import Base, get_db  # noqa: E402
from app.main import app  # noqa: E402
from app.models.user import User, UserRole  # noqa: E402
from app.services.demo_seed_service import DemoSeedService  # noqa: E402


engine = create_async_engine(test_database_url, pool_pre_ping=True)
TestSession = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture(autouse=True)
async def reset_database() -> AsyncGenerator[None, None]:
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)
        await connection.run_sync(Base.metadata.create_all)
    yield
    async with engine.begin() as connection:
        await connection.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    async with TestSession() as session:
        yield session


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient, None]:
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        async with TestSession() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
async def admin_user(db_session: AsyncSession) -> User:
    user = User(
        email="admin.test@example.com",
        password_hash=hash_password("test-password"),
        role=UserRole.ADMIN,
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
async def support_agent(db_session: AsyncSession) -> User:
    user = User(
        email="agent.test@example.com",
        password_hash=hash_password("test-password"),
        role=UserRole.SUPPORT_AGENT,
        is_active=True,
    )
    db_session.add(user)
    await db_session.commit()
    await db_session.refresh(user)
    return user


@pytest.fixture
def auth_headers(admin_user: User) -> dict[str, str]:
    token, _ = create_access_token(admin_user.id, admin_user.role)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
def support_agent_headers(support_agent: User) -> dict[str, str]:
    token, _ = create_access_token(support_agent.id, support_agent.role)
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture
async def seeded_ticket_ids(db_session: AsyncSession) -> dict[str, UUID]:
    await DemoSeedService(db_session).seed()
    return DemoSeedService._TICKET_IDS


@pytest.fixture(scope="session", autouse=True)
async def dispose_engine() -> AsyncGenerator[None, None]:
    yield
    await engine.dispose()
