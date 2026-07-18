"""initial schema

Revision ID: 5e77df26f90e
Revises:
Create Date: 2026-07-18 18:59:03.116851

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "5e77df26f90e"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

customer_tier_enum = postgresql.ENUM(
    "standard",
    "premium",
    "vip",
    name="customertier",
    create_type=False,
)
account_status_enum = postgresql.ENUM(
    "active",
    "suspended",
    "cancelled",
    name="accountstatus",
    create_type=False,
)
order_status_enum = postgresql.ENUM(
    "placed",
    "shipped",
    "delivered",
    "refunded",
    "cancelled",
    name="orderstatus",
    create_type=False,
)
ticket_priority_enum = postgresql.ENUM(
    "low",
    "medium",
    "high",
    "critical",
    name="ticketpriority",
    create_type=False,
)
ticket_status_enum = postgresql.ENUM(
    "open",
    "in_progress",
    "resolved",
    "closed",
    name="ticketstatus",
    create_type=False,
)
resolution_status_enum = postgresql.ENUM(
    "pending",
    "approved",
    "rejected",
    name="resolutionstatus",
    create_type=False,
)


def upgrade() -> None:
    """Create initial ACRA schema."""
    bind = op.get_bind()
    customer_tier_enum.create(bind, checkfirst=True)
    account_status_enum.create(bind, checkfirst=True)
    order_status_enum.create(bind, checkfirst=True)
    ticket_priority_enum.create(bind, checkfirst=True)
    ticket_status_enum.create(bind, checkfirst=True)
    resolution_status_enum.create(bind, checkfirst=True)

    op.create_table(
        "customers",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("full_name", sa.String(length=255), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("phone", sa.String(length=50), nullable=True),
        sa.Column(
            "tier",
            customer_tier_enum,
            server_default="standard",
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_customers_email", "customers", ["email"], unique=True)

    op.create_table(
        "accounts",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("customer_id", sa.UUID(), nullable=False),
        sa.Column("plan_type", sa.String(length=100), nullable=False),
        sa.Column(
            "status",
            account_status_enum,
            server_default="active",
            nullable=False,
        ),
        sa.Column("signup_date", sa.Date(), nullable=False),
        sa.Column("billing_cycle", sa.String(length=50), nullable=False),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("customer_id"),
    )

    op.create_table(
        "orders",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("customer_id", sa.UUID(), nullable=False),
        sa.Column("product_name", sa.String(length=255), nullable=False),
        sa.Column("amount", sa.Numeric(precision=10, scale=2), nullable=False),
        sa.Column(
            "currency",
            sa.String(length=10),
            server_default="USD",
            nullable=False,
        ),
        sa.Column(
            "status",
            order_status_enum,
            server_default="placed",
            nullable=False,
        ),
        sa.Column(
            "order_date",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("delivery_eta", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_table(
        "tickets",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("customer_id", sa.UUID(), nullable=False),
        sa.Column("order_id", sa.UUID(), nullable=True),
        sa.Column("subject", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("category", sa.String(length=100), nullable=True),
        sa.Column(
            "priority",
            ticket_priority_enum,
            server_default="medium",
            nullable=False,
        ),
        sa.Column(
            "status",
            ticket_status_enum,
            server_default="open",
            nullable=False,
        ),
        sa.Column("sentiment", sa.String(length=50), nullable=True),
        sa.Column("intent", sa.String(length=100), nullable=True),
        sa.Column("ai_summary", sa.Text(), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["customer_id"], ["customers.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["order_id"], ["orders.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_tickets_customer_id", "tickets", ["customer_id"], unique=False)
    op.create_index("ix_tickets_order_id", "tickets", ["order_id"], unique=False)

    op.create_table(
        "resolutions",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("ticket_id", sa.UUID(), nullable=False),
        sa.Column(
            "generated_response",
            sa.Text(),
            nullable=True,
            comment="Full AI-generated response text proposed for the customer.",
        ),
        sa.Column(
            "confidence_score",
            sa.Float(),
            nullable=True,
            comment="Model confidence in the generated response, range 0.0 – 1.0.",
        ),
        sa.Column(
            "escalation_required",
            sa.Boolean(),
            server_default=sa.text("false"),
            nullable=False,
            comment="True when the AI determines a human agent must handle the ticket.",
        ),
        sa.Column(
            "resolution_status",
            resolution_status_enum,
            server_default="pending",
            nullable=False,
            comment="Approval state of the resolution in the review workflow.",
        ),
        sa.Column(
            "model_name",
            sa.String(length=150),
            nullable=True,
            comment="Identifier of the AI model that generated this resolution.",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["ticket_id"], ["tickets.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_resolutions_ticket_id",
        "resolutions",
        ["ticket_id"],
        unique=False,
    )


def downgrade() -> None:
    """Drop initial ACRA schema."""
    bind = op.get_bind()

    op.drop_index("ix_resolutions_ticket_id", table_name="resolutions")
    op.drop_table("resolutions")

    op.drop_index("ix_tickets_order_id", table_name="tickets")
    op.drop_index("ix_tickets_customer_id", table_name="tickets")
    op.drop_table("tickets")

    op.drop_table("orders")
    op.drop_table("accounts")

    op.drop_index("ix_customers_email", table_name="customers")
    op.drop_table("customers")

    resolution_status_enum.drop(bind, checkfirst=True)
    ticket_status_enum.drop(bind, checkfirst=True)
    ticket_priority_enum.drop(bind, checkfirst=True)
    order_status_enum.drop(bind, checkfirst=True)
    account_status_enum.drop(bind, checkfirst=True)
    customer_tier_enum.drop(bind, checkfirst=True)
