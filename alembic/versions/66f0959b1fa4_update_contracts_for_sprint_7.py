"""update contracts for sprint 7

Revision ID: 66f0959b1fa4
Revises: 40e1ed3bff29
Create Date: 2026-08-14 19:51:00.764236
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "66f0959b1fa4"
down_revision: Union[str, Sequence[str], None] = "40e1ed3bff29"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Rename existing contract_name column to title
    op.alter_column(
        "contracts",
        "contract_name",
        new_column_name="title",
        existing_type=sa.String(length=200),
        existing_nullable=False
    )

    # Add new columns temporarily as nullable
    op.add_column(
        "contracts",
        sa.Column(
            "contract_number",
            sa.String(length=100),
            nullable=True
        )
    )

    op.add_column(
        "contracts",
        sa.Column(
            "category",
            sa.String(length=100),
            nullable=True
        )
    )

    # Add timestamps
    op.add_column(
        "contracts",
        sa.Column(
            "created_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False
        )
    )

    op.add_column(
        "contracts",
        sa.Column(
            "updated_at",
            sa.DateTime(),
            server_default=sa.text("now()"),
            nullable=False
        )
    )

    # Fill existing contracts with Sprint 7 data
    op.execute("""
        UPDATE contracts
        SET
            contract_number = 'CNT-100' || id,
            category = CASE
                WHEN id = 1 THEN 'Service Agreement'
                WHEN id = 2 THEN 'Vendor Contract'
                WHEN id = 3 THEN 'Vendor Contract'
                ELSE 'Service Agreement'
            END
    """)

    # Make new fields required
    op.alter_column(
        "contracts",
        "contract_number",
        existing_type=sa.String(length=100),
        nullable=False
    )

    op.alter_column(
        "contracts",
        "category",
        existing_type=sa.String(length=100),
        nullable=False
    )

    # Make contract number unique
    op.create_index(
        op.f("ix_contracts_contract_number"),
        "contracts",
        ["contract_number"],
        unique=True
    )


def downgrade() -> None:
    # Remove unique index
    op.drop_index(
        op.f("ix_contracts_contract_number"),
        table_name="contracts"
    )

    # Remove timestamps
    op.drop_column("contracts", "updated_at")
    op.drop_column("contracts", "created_at")

    # Remove Sprint 7 fields
    op.drop_column("contracts", "category")
    op.drop_column("contracts", "contract_number")

    # Rename title back to contract_name
    op.alter_column(
        "contracts",
        "title",
        new_column_name="contract_name",
        existing_type=sa.String(length=200),
        existing_nullable=False
    )