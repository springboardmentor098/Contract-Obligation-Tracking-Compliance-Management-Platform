"""update renewals table for sprint 10

Revision ID: a6a2ab85b9b4
Revises: 1ff81a4bff3a
Create Date: 2026-08-28 16:47:50.165024

"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a6a2ab85b9b4"
down_revision: Union[str, Sequence[str], None] = "1ff81a4bff3a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # ---------------------------------------------------------
    # 1. Add new columns as nullable first
    # ---------------------------------------------------------

    op.add_column(
        "renewals",
        sa.Column(
            "previous_expiry_date",
            sa.Date(),
            nullable=True
        )
    )

    op.add_column(
        "renewals",
        sa.Column(
            "new_expiry_date",
            sa.Date(),
            nullable=True
        )
    )

    op.add_column(
        "renewals",
        sa.Column(
            "assigned_to",
            sa.Integer(),
            nullable=True
        )
    )

    op.add_column(
        "renewals",
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=True
        )
    )

    op.add_column(
        "renewals",
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=True
        )
    )

    # ---------------------------------------------------------
    # 2. Populate existing renewal records
    # ---------------------------------------------------------

    # Use the contract's existing expiry date as the
    # previous expiry date for existing renewal records.
    op.execute(
        """
        UPDATE renewals r
        SET previous_expiry_date = c.end_date
        FROM contracts c
        WHERE r.contract_id = c.id
        AND r.previous_expiry_date IS NULL
        """
    )

    # For existing records, initially use the previous
    # expiry date as the new expiry date.
    op.execute(
        """
        UPDATE renewals
        SET new_expiry_date = previous_expiry_date
        WHERE new_expiry_date IS NULL
        """
    )

    # Use the contract's assigned user for existing renewals.
    op.execute(
        """
        UPDATE renewals r
        SET assigned_to = c.assigned_to
        FROM contracts c
        WHERE r.contract_id = c.id
        AND r.assigned_to IS NULL
        """
    )

    # Set timestamps for existing records.
    op.execute(
        """
        UPDATE renewals
        SET created_at = CURRENT_TIMESTAMP
        WHERE created_at IS NULL
        """
    )

    op.execute(
        """
        UPDATE renewals
        SET updated_at = CURRENT_TIMESTAMP
        WHERE updated_at IS NULL
        """
    )

    # ---------------------------------------------------------
    # 3. Make required columns NOT NULL
    # ---------------------------------------------------------

    op.alter_column(
        "renewals",
        "previous_expiry_date",
        existing_type=sa.Date(),
        nullable=False
    )

    op.alter_column(
        "renewals",
        "new_expiry_date",
        existing_type=sa.Date(),
        nullable=False
    )

    op.alter_column(
        "renewals",
        "assigned_to",
        existing_type=sa.Integer(),
        nullable=False
    )

    op.alter_column(
        "renewals",
        "created_at",
        existing_type=sa.DateTime(),
        nullable=False
    )

    op.alter_column(
        "renewals",
        "updated_at",
        existing_type=sa.DateTime(),
        nullable=False
    )

    # ---------------------------------------------------------
    # 4. Add foreign key for assigned_to
    # ---------------------------------------------------------

    op.create_foreign_key(
        "fk_renewals_assigned_to_users",
        "renewals",
        "users",
        ["assigned_to"],
        ["id"]
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_constraint(
        "fk_renewals_assigned_to_users",
        "renewals",
        type_="foreignkey"
    )

    op.drop_column(
        "renewals",
        "updated_at"
    )

    op.drop_column(
        "renewals",
        "created_at"
    )

    op.drop_column(
        "renewals",
        "assigned_to"
    )

    op.drop_column(
        "renewals",
        "new_expiry_date"
    )

    op.drop_column(
        "renewals",
        "previous_expiry_date"
    )