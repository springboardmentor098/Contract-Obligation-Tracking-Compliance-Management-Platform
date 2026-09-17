"""create obligations table

Revision ID: 9d94f40b2373
Revises: e1c3690e562b
Create Date: 2026-08-19 23:44:08.597068

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "9d94f40b2373"
down_revision: Union[str, Sequence[str], None] = "e1c3690e562b"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # Add completion date
    op.add_column(
        "obligations",
        sa.Column(
            "completion_date",
            sa.Date(),
            nullable=True
        )
    )

    # Add updated_at timestamp
    op.add_column(
        "obligations",
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False
        )
    )

    # Add index for assigned user
    op.create_index(
        op.f("ix_obligations_assigned_to"),
        "obligations",
        ["assigned_to"],
        unique=False
    )

    # Add index for contract
    op.create_index(
        op.f("ix_obligations_contract_id"),
        "obligations",
        ["contract_id"],
        unique=False
    )

    # Remove old fields
    op.drop_column(
        "obligations",
        "completed_at"
    )

    op.drop_column(
        "obligations",
        "compliance_status"
    )


def downgrade() -> None:
    """Downgrade schema."""

    # Restore old fields
    op.add_column(
        "obligations",
        sa.Column(
            "compliance_status",
            sa.VARCHAR(length=50),
            nullable=False
        )
    )

    op.add_column(
        "obligations",
        sa.Column(
            "completed_at",
            sa.DateTime(),
            nullable=True
        )
    )

    # Remove indexes
    op.drop_index(
        op.f("ix_obligations_contract_id"),
        table_name="obligations"
    )

    op.drop_index(
        op.f("ix_obligations_assigned_to"),
        table_name="obligations"
    )

    # Remove new fields
    op.drop_column(
        "obligations",
        "updated_at"
    )

    op.drop_column(
        "obligations",
        "completion_date"
    )