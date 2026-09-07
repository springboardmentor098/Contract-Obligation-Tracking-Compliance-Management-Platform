"""add password to users

Revision ID: 092a470abe73
Revises: cf953fb2c6fb
Create Date: 2026-08-25 22:48:06.207883

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "092a470abe73"
down_revision: Union[str, Sequence[str], None] = "cf953fb2c6fb"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add password column to users table."""
    op.add_column(
        "users",
        sa.Column("password", sa.String(length=255), nullable=False)
    )


def downgrade() -> None:
    """Remove password column from users table."""
    op.drop_column("users", "password")