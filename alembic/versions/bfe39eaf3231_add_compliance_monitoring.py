"""add compliance monitoring

Revision ID: bfe39eaf3231
Revises: 8aecb36ed724
Create Date: 2026-08-26 23:03:00.950963
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "bfe39eaf3231"

down_revision: Union[str, Sequence[str], None] = "8aecb36ed724"

branch_labels: Union[str, Sequence[str], None] = None

depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # =========================================================
    # CREATE CONTRACT COMPLIANCE TABLE
    # =========================================================

    op.create_table(
        "contract_compliance",

        sa.Column(
            "id",
            sa.Integer(),
            nullable=False
        ),

        sa.Column(
            "contract_id",
            sa.Integer(),
            nullable=False
        ),

        sa.Column(
            "status",
            sa.String(),
            nullable=False
        ),

        sa.Column(
            "compliance_score",
            sa.Float(),
            nullable=False
        ),

        sa.Column(
            "risk_level",
            sa.String(),
            nullable=False
        ),

        sa.Column(
            "notes",
            sa.Text(),
            nullable=True
        ),

        sa.Column(
            "evaluated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False
        ),

        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False
        ),

        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False
        ),

        sa.ForeignKeyConstraint(
            ["contract_id"],
            ["contracts.id"],
            ondelete="CASCADE"
        ),

        sa.PrimaryKeyConstraint("id")
    )

    # =========================================================
    # CREATE INDEXES
    # =========================================================

    op.create_index(
        op.f("ix_contract_compliance_contract_id"),
        "contract_compliance",
        ["contract_id"],
        unique=False
    )

    op.create_index(
        op.f("ix_contract_compliance_id"),
        "contract_compliance",
        ["id"],
        unique=False
    )


def downgrade() -> None:
    """Downgrade schema."""

    # =========================================================
    # DROP INDEXES
    # =========================================================

    op.drop_index(
        op.f("ix_contract_compliance_id"),
        table_name="contract_compliance"
    )

    op.drop_index(
        op.f("ix_contract_compliance_contract_id"),
        table_name="contract_compliance"
    )

    # =========================================================
    # DROP TABLE
    # =========================================================

    op.drop_table("contract_compliance")