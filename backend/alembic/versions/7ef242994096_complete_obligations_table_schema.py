"""complete obligations table schema

Revision ID: 7ef242994096
Revises: cea1b186aeed
Create Date: 2026-08-21 16:18:06.225589

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "7ef242994096"
down_revision: Union[str, Sequence[str], None] = "cea1b186aeed"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # Add missing columns to obligations table

    op.add_column(
        "obligations",
        sa.Column(
            "title",
            sa.String(length=255),
            nullable=True
        )
    )

    op.add_column(
        "obligations",
        sa.Column(
            "obligation_type",
            sa.String(length=100),
            nullable=True
        )
    )

    op.add_column(
        "obligations",
        sa.Column(
            "completion_date",
            sa.Date(),
            nullable=True
        )
    )

    op.add_column(
        "obligations",
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=True
        )
    )

    op.add_column(
        "obligations",
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=True
        )
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_column(
        "obligations",
        "updated_at"
    )

    op.drop_column(
        "obligations",
        "created_at"
    )

    op.drop_column(
        "obligations",
        "completion_date"
    )

    op.drop_column(
        "obligations",
        "obligation_type"
    )

    op.drop_column(
        "obligations",
        "title"
    )