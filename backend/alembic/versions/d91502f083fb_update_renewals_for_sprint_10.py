"""update renewals for sprint 10

Revision ID: d91502f083fb
Revises: ba82f70ed3f1
Create Date: 2026-08-27

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "d91502f083fb"
down_revision: Union[str, Sequence[str], None] = "ba82f70ed3f1"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # Rename existing columns instead of dropping them.
    # This preserves existing renewal data.

    op.alter_column(
        "renewals",
        "initiated_by",
        new_column_name="assigned_to",
        existing_type=sa.UUID(),
        existing_nullable=False,
    )

    op.alter_column(
        "renewals",
        "previous_end_date",
        new_column_name="previous_expiry_date",
        existing_type=sa.Date(),
        existing_nullable=True,
    )

    op.alter_column(
        "renewals",
        "new_end_date",
        new_column_name="new_expiry_date",
        existing_type=sa.Date(),
        existing_nullable=True,
    )

    # Replace the old foreign key with the new assigned_to foreign key.
    op.drop_constraint(
        "renewals_initiated_by_fkey",
        "renewals",
        type_="foreignkey",
    )

    op.create_foreign_key(
        "renewals_assigned_to_fkey",
        "renewals",
        "users",
        ["assigned_to"],
        ["id"],
    )

    # Existing renewal records may have NULL status.
    # Give them the Sprint 10 default before enforcing NOT NULL.
    op.execute(
        "UPDATE renewals SET status = 'Upcoming' WHERE status IS NULL"
    )

    op.alter_column(
        "renewals",
        "status",
        existing_type=sa.String(length=50),
        nullable=False,
        server_default="Upcoming",
    )


def downgrade() -> None:
    """Downgrade schema."""

    # Remove the Sprint 10 foreign key.
    op.drop_constraint(
        "renewals_assigned_to_fkey",
        "renewals",
        type_="foreignkey",
    )

    # Restore the original foreign key.
    op.create_foreign_key(
        "renewals_initiated_by_fkey",
        "renewals",
        "users",
        ["assigned_to"],
        ["id"],
    )

    # Restore nullable status behavior.
    op.alter_column(
        "renewals",
        "status",
        existing_type=sa.String(length=50),
        nullable=True,
        server_default=None,
    )

    # Rename columns back to their original names.
    op.alter_column(
        "renewals",
        "assigned_to",
        new_column_name="initiated_by",
        existing_type=sa.UUID(),
        existing_nullable=False,
    )

    op.alter_column(
        "renewals",
        "previous_expiry_date",
        new_column_name="previous_end_date",
        existing_type=sa.Date(),
        existing_nullable=True,
    )

    op.alter_column(
        "renewals",
        "new_expiry_date",
        new_column_name="new_end_date",
        existing_type=sa.Date(),
        existing_nullable=True,
    )