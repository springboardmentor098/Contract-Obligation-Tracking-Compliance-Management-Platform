"""update renewals table for sprint 10

Revision ID: 8aecb36ed724
Revises: 9d94f40b2373
Create Date: 2026-08-26 22:16:37.507343

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "8aecb36ed724"
down_revision: Union[str, Sequence[str], None] = "9d94f40b2373"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # Add previous expiry date to renewals
    op.add_column(
        "renewals",
        sa.Column(
            "previous_expiry_date",
            sa.Date(),
            nullable=False
        )
    )

    # Add user responsible for the renewal
    op.add_column(
        "renewals",
        sa.Column(
            "assigned_to",
            sa.Integer(),
            nullable=True
        )
    )

    # Add updated timestamp
    op.add_column(
        "renewals",
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=True
        )
    )

    # Add index for contract_id
    op.create_index(
        op.f("ix_renewals_contract_id"),
        "renewals",
        ["contract_id"],
        unique=False
    )

    # Remove old approved_by foreign key
    op.drop_constraint(
        op.f("renewals_approved_by_fkey"),
        "renewals",
        type_="foreignkey"
    )

    # Add assigned_to foreign key
    op.create_foreign_key(
        "renewals_assigned_to_fkey",
        "renewals",
        "users",
        ["assigned_to"],
        ["id"]
    )

    # Remove old approved_by column
    op.drop_column(
        "renewals",
        "approved_by"
    )


def downgrade() -> None:
    """Downgrade schema."""

    # Add approved_by column back
    op.add_column(
        "renewals",
        sa.Column(
            "approved_by",
            sa.Integer(),
            nullable=True
        )
    )

    # Remove assigned_to foreign key
    op.drop_constraint(
        "renewals_assigned_to_fkey",
        "renewals",
        type_="foreignkey"
    )

    # Recreate approved_by foreign key
    op.create_foreign_key(
        "renewals_approved_by_fkey",
        "renewals",
        "users",
        ["approved_by"],
        ["id"]
    )

    # Remove contract_id index
    op.drop_index(
        op.f("ix_renewals_contract_id"),
        table_name="renewals"
    )

    # Remove updated_at
    op.drop_column(
        "renewals",
        "updated_at"
    )

    # Remove assigned_to
    op.drop_column(
        "renewals",
        "assigned_to"
    )

    # Remove previous_expiry_date
    op.drop_column(
        "renewals",
        "previous_expiry_date"
    )