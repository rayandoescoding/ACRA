from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.account import Account
from app.models.customer import Customer
from app.models.order import Order
from app.models.ticket import Ticket
from app.services.demo_seed_service import DemoSeedService


async def record_count(session: AsyncSession, model) -> int:
    return await session.scalar(select(func.count()).select_from(model)) or 0


async def test_demo_seed_is_idempotent_and_creates_expected_records(db_session: AsyncSession) -> None:
    first_result = await DemoSeedService(db_session).seed()
    second_result = await DemoSeedService(db_session).seed()

    assert first_result.customers_created == 5
    assert first_result.accounts_created == 5
    assert first_result.orders_created == 8
    assert first_result.tickets_created == 10
    assert second_result.customers_created == 0
    assert second_result.accounts_created == 0
    assert second_result.orders_created == 0
    assert second_result.tickets_created == 0
    assert await record_count(db_session, Customer) == 5
    assert await record_count(db_session, Account) == 5
    assert await record_count(db_session, Order) == 8
    assert await record_count(db_session, Ticket) == 10
