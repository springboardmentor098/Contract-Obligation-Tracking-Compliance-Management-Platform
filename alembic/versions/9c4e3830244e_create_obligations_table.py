"""create obligations table

Revision ID: 9c4e3830244e
Revises: a02d01ca2bde
Create Date: 2026-08-19 18:44:56.953923

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "9c4e3830244e"
down_revision: Union[str, Sequence[str], None] = "a02d01ca2bde"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # ============================================================
    # ADD OBLIGATION TYPE
    # ============================================================

    op.add_column(
        "obligations",
        sa.Column(
            "obligation_type",
            sa.String(length=100),
            nullable=True
        )
    )

    # ============================================================
    # ADD COMPLETION DATE
    # ============================================================

    op.add_column(
        "obligations",
        sa.Column(
            "completion_date",
            sa.Date(),
            nullable=True
        )
    )

    # ============================================================
    # UPDATE DUE DATE
    # ============================================================

    op.alter_column(
        "obligations",
        "due_date",
        existing_type=sa.Date(),
        nullable=False
    )

    # ============================================================
    # UPDATE STATUS
    # ============================================================

    op.alter_column(
        "obligations",
        "status",
        existing_type=sa.String(length=50),
        nullable=False
    )

    # ============================================================
    # UPDATE TIMESTAMPS
    # ============================================================

    op.alter_column(
        "obligations",
        "created_at",
        existing_type=sa.DateTime(),
        nullable=False
    )

    op.alter_column(
        "obligations",
        "updated_at",
        existing_type=sa.DateTime(),
        nullable=False
    )

    # ============================================================
    # SET DEFAULT STATUS
    # ============================================================

    op.alter_column(
        "obligations",
        "status",
        existing_type=sa.String(length=50),
        server_default="Pending"
    )


def downgrade() -> None:
    """Downgrade schema."""

    # Remove default
    op.alter_column(
        "obligations",
        "status",
        existing_type=sa.String(length=50),
        server_default=None
    )

    # Restore nullable fields
    op.alter_column(
        "obligations",
        "updated_at",
        existing_type=sa.DateTime(),
        nullable=True
    )

    op.alter_column(
        "obligations",
        "created_at",
        existing_type=sa.DateTime(),
        nullable=True
    )

    op.alter_column(
        "obligations",
        "status",
        existing_type=sa.String(length=50),
        nullable=True
    )

    op.alter_column(
        "obligations",
        "due_date",
        existing_type=sa.Date(),
        nullable=True
    )

    # Remove Sprint 9 columns
    op.drop_column(
        "obligations",
        "completion_date"
    )

    op.drop_column(
        "obligations",
        "obligation_type"
    )