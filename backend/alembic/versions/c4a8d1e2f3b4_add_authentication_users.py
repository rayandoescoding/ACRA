"""add authentication users

Revision ID: c4a8d1e2f3b4
Revises: 5e77df26f90e
Create Date: 2026-07-19
"""

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = "c4a8d1e2f3b4"
down_revision: Union[str, Sequence[str], None] = "5e77df26f90e"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


user_role_enum = postgresql.ENUM(
    "admin",
    "support_agent",
    name="userrole",
    create_type=False,
)


def upgrade() -> None:
    """Create the internal users table and role enum."""
    bind = op.get_bind()
    user_role_enum.create(bind, checkfirst=True)
    op.create_table(
        "users",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("password_hash", sa.String(length=255), nullable=False),
        sa.Column(
            "role",
            user_role_enum,
            server_default="support_agent",
            nullable=False,
        ),
        sa.Column(
            "is_active",
            sa.Boolean(),
            server_default=sa.text("true"),
            nullable=False,
        ),
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
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_users_email", "users", ["email"], unique=True)


def downgrade() -> None:
    """Remove authentication storage."""
    bind = op.get_bind()
    op.drop_index("ix_users_email", table_name="users")
    op.drop_table("users")
    user_role_enum.drop(bind, checkfirst=True)
