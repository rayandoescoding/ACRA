"""Deterministic local-demo data for exercising the ticket-processing pipeline."""

from dataclasses import dataclass
from datetime import date, datetime, timedelta
from decimal import Decimal
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.account import Account, AccountStatus
from app.models.customer import Customer, CustomerTier
from app.models.order import Order, OrderStatus
from app.models.ticket import Ticket, TicketStatus


@dataclass(frozen=True, slots=True)
class DemoSeedResult:
    """Counts of records newly created by one idempotent seed run."""

    customers_created: int
    accounts_created: int
    orders_created: int
    tickets_created: int

    @property
    def created_any(self) -> bool:
        """Return whether this invocation inserted at least one demo record."""
        return any(
            (
                self.customers_created,
                self.accounts_created,
                self.orders_created,
                self.tickets_created,
            )
        )


class DemoSeedService:
    """Create a stable, relationship-valid dataset without overwriting records."""

    _CUSTOMER_IDS = {
        "alice": UUID("10000000-0000-0000-0000-000000000001"),
        "bruno": UUID("10000000-0000-0000-0000-000000000002"),
        "chloe": UUID("10000000-0000-0000-0000-000000000003"),
        "diego": UUID("10000000-0000-0000-0000-000000000004"),
        "elena": UUID("10000000-0000-0000-0000-000000000005"),
    }
    _ACCOUNT_IDS = {
        "alice": UUID("20000000-0000-0000-0000-000000000001"),
        "bruno": UUID("20000000-0000-0000-0000-000000000002"),
        "chloe": UUID("20000000-0000-0000-0000-000000000003"),
        "diego": UUID("20000000-0000-0000-0000-000000000004"),
        "elena": UUID("20000000-0000-0000-0000-000000000005"),
    }
    _ORDER_IDS = {
        "eligible_refund": UUID("30000000-0000-0000-0000-000000000001"),
        "high_value_refund": UUID("30000000-0000-0000-0000-000000000002"),
        "vip_product": UUID("30000000-0000-0000-0000-000000000003"),
        "billing": UUID("30000000-0000-0000-0000-000000000004"),
        "delivery_delay": UUID("30000000-0000-0000-0000-000000000005"),
        "wrong_product": UUID("30000000-0000-0000-0000-000000000006"),
        "cancellation": UUID("30000000-0000-0000-0000-000000000007"),
        "feedback": UUID("30000000-0000-0000-0000-000000000008"),
    }
    _TICKET_IDS = {
        "eligible_refund": UUID("40000000-0000-0000-0000-000000000001"),
        "high_value_refund": UUID("40000000-0000-0000-0000-000000000002"),
        "angry_vip": UUID("40000000-0000-0000-0000-000000000003"),
        "billing": UUID("40000000-0000-0000-0000-000000000004"),
        "delivery_delay": UUID("40000000-0000-0000-0000-000000000005"),
        "wrong_product": UUID("40000000-0000-0000-0000-000000000006"),
        "account_access": UUID("40000000-0000-0000-0000-000000000007"),
        "cancellation": UUID("40000000-0000-0000-0000-000000000008"),
        "missing_information": UUID("40000000-0000-0000-0000-000000000009"),
        "positive_feedback": UUID("40000000-0000-0000-0000-000000000010"),
    }

    def __init__(self, db: AsyncSession) -> None:
        self._db = db
        self._resolved_customer_ids = dict(self._CUSTOMER_IDS)

    async def seed(self) -> DemoSeedResult:
        """Create missing demo records and leave any existing records unchanged."""
        reference_time = datetime.utcnow().replace(microsecond=0)
        customers_created = await self._seed_customers()
        accounts_created = await self._seed_accounts()
        orders_created = await self._seed_orders(reference_time)
        tickets_created = await self._seed_tickets()

        result = DemoSeedResult(
            customers_created=customers_created,
            accounts_created=accounts_created,
            orders_created=orders_created,
            tickets_created=tickets_created,
        )
        if result.created_any:
            await self._db.commit()
        return result

    async def _seed_customers(self) -> int:
        customers = (
            Customer(
                id=self._CUSTOMER_IDS["alice"],
                full_name="Alice Carter",
                email="alice.carter.demo@example.com",
                phone="+1-555-0101",
                tier=CustomerTier.STANDARD,
            ),
            Customer(
                id=self._CUSTOMER_IDS["bruno"],
                full_name="Bruno Singh",
                email="bruno.singh.demo@example.com",
                phone="+1-555-0102",
                tier=CustomerTier.VIP,
            ),
            Customer(
                id=self._CUSTOMER_IDS["chloe"],
                full_name="Chloe Martin",
                email="chloe.martin.demo@example.com",
                phone="+1-555-0103",
                tier=CustomerTier.PREMIUM,
            ),
            Customer(
                id=self._CUSTOMER_IDS["diego"],
                full_name="Diego Alvarez",
                email="diego.alvarez.demo@example.com",
                phone="+1-555-0104",
                tier=CustomerTier.STANDARD,
            ),
            Customer(
                id=self._CUSTOMER_IDS["elena"],
                full_name="Elena Brooks",
                email="elena.brooks.demo@example.com",
                phone="+1-555-0105",
                tier=CustomerTier.PREMIUM,
            ),
        )
        created = 0
        for key, customer in zip(self._CUSTOMER_IDS, customers, strict=True):
            existing_customer = await self._db.get(Customer, customer.id)
            if existing_customer is None:
                existing_customer = await self._db.scalar(
                    select(Customer).where(Customer.email == customer.email)
                )

            if existing_customer is None:
                self._db.add(customer)
                created += 1
            else:
                self._resolved_customer_ids[key] = existing_customer.id

        return created

    async def _seed_accounts(self) -> int:
        accounts = (
            Account(
                id=self._ACCOUNT_IDS["alice"],
                customer_id=self._resolved_customer_ids["alice"],
                plan_type="Basic",
                status=AccountStatus.ACTIVE,
                signup_date=date(2024, 2, 1),
                billing_cycle="monthly",
            ),
            Account(
                id=self._ACCOUNT_IDS["bruno"],
                customer_id=self._resolved_customer_ids["bruno"],
                plan_type="Enterprise",
                status=AccountStatus.ACTIVE,
                signup_date=date(2022, 6, 15),
                billing_cycle="annual",
            ),
            Account(
                id=self._ACCOUNT_IDS["chloe"],
                customer_id=self._resolved_customer_ids["chloe"],
                plan_type="Premium",
                status=AccountStatus.ACTIVE,
                signup_date=date(2023, 9, 10),
                billing_cycle="monthly",
            ),
            Account(
                id=self._ACCOUNT_IDS["diego"],
                customer_id=self._resolved_customer_ids["diego"],
                plan_type="Basic",
                status=AccountStatus.ACTIVE,
                signup_date=date(2025, 1, 20),
                billing_cycle="monthly",
            ),
            Account(
                id=self._ACCOUNT_IDS["elena"],
                customer_id=self._resolved_customer_ids["elena"],
                plan_type="Premium",
                status=AccountStatus.ACTIVE,
                signup_date=date(2024, 5, 5),
                billing_cycle="annual",
            ),
        )
        created = 0
        for account in accounts:
            existing_account = await self._db.get(Account, account.id)
            if existing_account is None:
                existing_account = await self._db.scalar(
                    select(Account).where(Account.customer_id == account.customer_id)
                )

            if existing_account is None:
                self._db.add(account)
                created += 1

        return created

    async def _seed_orders(self, reference_time: datetime) -> int:
        orders = (
            Order(
                id=self._ORDER_IDS["eligible_refund"],
                customer_id=self._resolved_customer_ids["alice"],
                product_name="Wireless Headphones",
                amount=Decimal("79.00"),
                currency="USD",
                status=OrderStatus.DELIVERED,
                order_date=reference_time - timedelta(days=7),
            ),
            Order(
                id=self._ORDER_IDS["high_value_refund"],
                customer_id=self._resolved_customer_ids["bruno"],
                product_name="Enterprise Analytics Subscription",
                amount=Decimal("1250.00"),
                currency="USD",
                status=OrderStatus.DELIVERED,
                order_date=reference_time - timedelta(days=3),
            ),
            Order(
                id=self._ORDER_IDS["vip_product"],
                customer_id=self._resolved_customer_ids["bruno"],
                product_name="Smart Home Hub",
                amount=Decimal("249.00"),
                currency="USD",
                status=OrderStatus.DELIVERED,
                order_date=reference_time - timedelta(days=10),
            ),
            Order(
                id=self._ORDER_IDS["billing"],
                customer_id=self._resolved_customer_ids["chloe"],
                product_name="Cloud Storage Plan",
                amount=Decimal("89.00"),
                currency="USD",
                status=OrderStatus.SHIPPED,
                order_date=reference_time - timedelta(days=14),
            ),
            Order(
                id=self._ORDER_IDS["delivery_delay"],
                customer_id=self._resolved_customer_ids["chloe"],
                product_name="Ergonomic Keyboard",
                amount=Decimal("119.00"),
                currency="USD",
                status=OrderStatus.SHIPPED,
                order_date=reference_time - timedelta(days=9),
                delivery_eta=reference_time - timedelta(days=2),
            ),
            Order(
                id=self._ORDER_IDS["wrong_product"],
                customer_id=self._resolved_customer_ids["diego"],
                product_name="Mechanical Keyboard",
                amount=Decimal("169.00"),
                currency="USD",
                status=OrderStatus.DELIVERED,
                order_date=reference_time - timedelta(days=6),
            ),
            Order(
                id=self._ORDER_IDS["cancellation"],
                customer_id=self._resolved_customer_ids["elena"],
                product_name="Monthly Design Toolkit",
                amount=Decimal("35.00"),
                currency="USD",
                status=OrderStatus.PLACED,
                order_date=reference_time - timedelta(days=1),
            ),
            Order(
                id=self._ORDER_IDS["feedback"],
                customer_id=self._resolved_customer_ids["elena"],
                product_name="Portable Monitor",
                amount=Decimal("299.00"),
                currency="USD",
                status=OrderStatus.DELIVERED,
                order_date=reference_time - timedelta(days=20),
            ),
        )
        return await self._add_missing(Order, orders)

    async def _seed_tickets(self) -> int:
        tickets = (
            Ticket(
                id=self._TICKET_IDS["eligible_refund"],
                customer_id=self._resolved_customer_ids["alice"],
                order_id=self._ORDER_IDS["eligible_refund"],
                subject="Refund request for wireless headphones",
                description="The headphones are defective and I would like a refund.",
                category="refund",
                status=TicketStatus.OPEN,
            ),
            Ticket(
                id=self._TICKET_IDS["high_value_refund"],
                customer_id=self._resolved_customer_ids["bruno"],
                order_id=self._ORDER_IDS["high_value_refund"],
                subject="Urgent refund request for enterprise subscription",
                description="I am frustrated and need a refund for this charge.",
                category="refund",
                status=TicketStatus.OPEN,
            ),
            Ticket(
                id=self._TICKET_IDS["angry_vip"],
                customer_id=self._resolved_customer_ids["bruno"],
                order_id=self._ORDER_IDS["vip_product"],
                subject="Angry VIP customer: smart hub not working",
                description="This product is broken and I am extremely disappointed.",
                category="product_issue",
                status=TicketStatus.OPEN,
            ),
            Ticket(
                id=self._TICKET_IDS["billing"],
                customer_id=self._resolved_customer_ids["chloe"],
                order_id=self._ORDER_IDS["billing"],
                subject="Incorrect billing charge",
                description="The invoice shows a charge I do not understand.",
                category="billing",
                status=TicketStatus.OPEN,
            ),
            Ticket(
                id=self._TICKET_IDS["delivery_delay"],
                customer_id=self._resolved_customer_ids["chloe"],
                order_id=self._ORDER_IDS["delivery_delay"],
                subject="Delivery is late",
                description="My package shipment is late and the delivery date has passed.",
                category="delivery",
                status=TicketStatus.OPEN,
            ),
            Ticket(
                id=self._TICKET_IDS["wrong_product"],
                customer_id=self._resolved_customer_ids["diego"],
                order_id=self._ORDER_IDS["wrong_product"],
                subject="Wrong product received",
                description="The item received is defective and not working as expected.",
                category="product_issue",
                status=TicketStatus.OPEN,
            ),
            Ticket(
                id=self._TICKET_IDS["account_access"],
                customer_id=self._resolved_customer_ids["diego"],
                subject="Account update and password access request",
                description="I cannot login and need to update my account password.",
                category="account_access",
                status=TicketStatus.OPEN,
            ),
            Ticket(
                id=self._TICKET_IDS["cancellation"],
                customer_id=self._resolved_customer_ids["elena"],
                order_id=self._ORDER_IDS["cancellation"],
                subject="Cancel my monthly toolkit order",
                description="Please cancel this subscription order before it ships.",
                category="cancellation",
                status=TicketStatus.OPEN,
            ),
            Ticket(
                id=self._TICKET_IDS["missing_information"],
                customer_id=self._resolved_customer_ids["elena"],
                subject="Need help with a recent request",
                description="Please help me with this request.",
                category="general_support",
                status=TicketStatus.OPEN,
            ),
            Ticket(
                id=self._TICKET_IDS["positive_feedback"],
                customer_id=self._resolved_customer_ids["elena"],
                order_id=self._ORDER_IDS["feedback"],
                subject="Excellent service feedback",
                description="Thanks for the excellent service and great support.",
                category="feedback",
                status=TicketStatus.OPEN,
            ),
        )
        return await self._add_missing(Ticket, tickets)

    async def _add_missing(
        self,
        model: type[Customer | Account | Order | Ticket],
        records: tuple[Customer | Account | Order | Ticket, ...],
    ) -> int:
        """Add only records whose fixed primary key is absent from the database."""
        created = 0
        for record in records:
            if await self._db.get(model, record.id) is None:
                self._db.add(record)
                created += 1
        return created
