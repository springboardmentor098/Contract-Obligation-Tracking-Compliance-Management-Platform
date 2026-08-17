"""update contracts for sprint 7

Revision ID: 2feb67cc5981
Revises: a3b28be216a3
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "2feb67cc5981"
down_revision: Union[str, Sequence[str], None] = "a3b28be216a3"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Rename existing columns instead of creating empty replacement columns.
    op.alter_column(
        "contracts",
        "owner_id",
        new_column_name="created_by",
    )

    op.alter_column(
        "contracts",
        "contract_type",
        new_column_name="category",
    )

    # Existing contracts may have NULL status.
    # Sprint 7 requires newly created contracts to start as Draft.
    op.execute(
        sa.text(
            "UPDATE contracts SET status = 'Draft' WHERE status IS NULL"
        )
    )

    op.alter_column(
        "contracts",
        "status",
        existing_type=sa.String(length=50),
        nullable=False,
    )

    # Existing contracts may have NULL category.
    # Give those existing records a valid category.
    op.execute(
        sa.text(
            "UPDATE contracts "
            "SET category = 'Service Agreement' "
            "WHERE category IS NULL"
        )
    )

    op.alter_column(
        "contracts",
        "category",
        existing_type=sa.String(length=100),
        nullable=False,
    )

    # Recreate the foreign key using the new column name.
    op.drop_constraint(
        "contracts_owner_id_fkey",
        "contracts",
        type_="foreignkey",
    )

    op.create_foreign_key(
        "contracts_created_by_fkey",
        "contracts",
        "users",
        ["created_by"],
        ["id"],
    )

    # Contract number must be unique.
    op.create_index(
        "ix_contracts_contract_number",
        "contracts",
        ["contract_number"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index(
        "ix_contracts_contract_number",
        table_name="contracts",
    )

    op.drop_constraint(
        "contracts_created_by_fkey",
        "contracts",
        type_="foreignkey",
    )

    op.create_foreign_key(
        "contracts_owner_id_fkey",
        "contracts",
        "users",
        ["created_by"],
        ["id"],
    )

    op.alter_column(
        "contracts",
        "category",
        existing_type=sa.String(length=100),
        nullable=True,
    )

    op.alter_column(
        "contracts",
        "status",
        existing_type=sa.String(length=50),
        nullable=True,
    )

    op.alter_column(
        "contracts",
        "category",
        new_column_name="contract_type",
    )

    op.alter_column(
        "contracts",
        "created_by",
        new_column_name="owner_id",
    )