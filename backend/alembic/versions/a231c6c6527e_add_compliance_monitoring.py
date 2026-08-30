"""add compliance monitoring

Revision ID: a231c6c6527e
Revises: d91502f083fb
Create Date: 2026-08-30 15:52:08.150429

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "a231c6c6527e"
down_revision: Union[str, Sequence[str], None] = "d91502f083fb"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Create compliance monitoring table."""

    op.create_table(
        "compliance",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "contract_id",
            postgresql.UUID(as_uuid=True),
            nullable=False,
        ),
        sa.Column(
            "compliance_score",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "total_obligations",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "completed_obligations",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "pending_obligations",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "overdue_obligations",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "delayed_obligations",
            sa.Integer(),
            nullable=False,
            server_default="0",
        ),
        sa.Column(
            "compliance_status",
            sa.String(length=50),
            nullable=False,
            server_default="Compliant",
        ),
        sa.Column(
            "risk_level",
            sa.String(length=50),
            nullable=False,
            server_default="Low",
        ),
        sa.Column(
            "notes",
            sa.Text(),
            nullable=True,
        ),
        sa.Column(
            "evaluated_at",
            sa.DateTime(),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["contract_id"],
            ["contracts.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    op.create_index(
        "ix_compliance_contract_id",
        "compliance",
        ["contract_id"],
        unique=False,
    )


def downgrade() -> None:
    """Drop compliance monitoring table."""

    op.drop_index(
        "ix_compliance_contract_id",
        table_name="compliance",
    )

    op.drop_table("compliance")