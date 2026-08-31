"""create renewals table

Revision ID: 90638d47dc9e
Revises: 0413c60a2f17
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "90638d47dc9e"
down_revision: Union[str, Sequence[str], None] = "0413c60a2f17"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add new columns as nullable first so existing rows are preserved.
    op.add_column(
        "renewals",
        sa.Column("previous_expiry_date", sa.Date(), nullable=True)
    )

    op.add_column(
        "renewals",
        sa.Column("new_expiry_date", sa.Date(), nullable=True)
    )

    op.add_column(
        "renewals",
        sa.Column("assigned_to", sa.Integer(), nullable=True)
    )

    # Copy the existing contract expiry date into previous_expiry_date
    # for existing renewal records.
    op.execute(
        """
        UPDATE renewals r
        SET previous_expiry_date = c.end_date
        FROM contracts c
        WHERE r.contract_id = c.id
          AND r.previous_expiry_date IS NULL
        """
    )

    # Existing renewal records must have a value before we make
    # previous_expiry_date NOT NULL.
    op.alter_column(
        "renewals",
        "previous_expiry_date",
        existing_type=sa.Date(),
        nullable=False
    )

    op.alter_column(
        "renewals",
        "status",
        existing_type=sa.VARCHAR(length=50),
        type_=sa.String(length=30),
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

    # Remove old created_by foreign key.
    op.drop_constraint(
        "renewals_created_by_fkey",
        "renewals",
        type_="foreignkey"
    )

    # Add assigned_to -> users.id
    op.create_foreign_key(
        "renewals_assigned_to_fkey",
        "renewals",
        "users",
        ["assigned_to"],
        ["id"]
    )

    # Remove old columns that are not part of Sprint 10.
    op.drop_column("renewals", "created_by")
    op.drop_column("renewals", "notice_date")


def downgrade() -> None:
    op.add_column(
        "renewals",
        sa.Column("notice_date", sa.Date(), nullable=True)
    )

    op.add_column(
        "renewals",
        sa.Column("created_by", sa.Integer(), nullable=True)
    )

    op.drop_constraint(
        "renewals_assigned_to_fkey",
        "renewals",
        type_="foreignkey"
    )

    op.create_foreign_key(
        "renewals_created_by_fkey",
        "renewals",
        "users",
        ["created_by"],
        ["id"]
    )

    op.alter_column(
        "renewals",
        "updated_at",
        existing_type=sa.DateTime(),
        nullable=True
    )

    op.alter_column(
        "renewals",
        "created_at",
        existing_type=sa.DateTime(),
        nullable=True
    )

    op.alter_column(
        "renewals",
        "status",
        existing_type=sa.String(length=30),
        type_=sa.VARCHAR(length=50),
        nullable=True
    )

    op.drop_column("renewals", "assigned_to")
    op.drop_column("renewals", "new_expiry_date")
    op.drop_column("renewals", "previous_expiry_date")
