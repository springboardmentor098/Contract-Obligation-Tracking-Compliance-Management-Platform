"""add missing contract workflow columns

Revision ID: 4b7c8d1e2f90
Revises: 33f88fc04dd8
Create Date: 2026-08-20 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "4b7c8d1e2f90"
down_revision: Union[str, Sequence[str], None] = "33f88fc04dd8"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("contracts", sa.Column("assigned_to", sa.Integer(), nullable=True))
    op.add_column(
        "contracts",
        sa.Column("reviewed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.add_column(
        "contracts",
        sa.Column("approved_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_foreign_key(
        "contracts_assigned_to_fkey",
        "contracts",
        "users",
        ["assigned_to"],
        ["id"],
        ondelete="SET NULL",
    )


def downgrade() -> None:
    op.drop_constraint("contracts_assigned_to_fkey", "contracts", type_="foreignkey")
    op.drop_column("contracts", "approved_at")
    op.drop_column("contracts", "reviewed_at")
    op.drop_column("contracts", "assigned_to")
