"""align contracts with workflow model

Revision ID: dd5e169a9f88
Revises: d29c0da7e156
Create Date: 2026-08-20

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "dd5e169a9f88"
down_revision: Union[str, Sequence[str], None] = "d29c0da7e156"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """
    Safely migrate the existing contracts table.

    Existing data:
        owner_id -> created_by
        owner_id -> assigned_to

    Existing counterparty_name is preserved.
    """

    # ---------------------------------------------------------
    # 1. Add new columns as nullable temporarily
    # ---------------------------------------------------------

    op.add_column(
        "contracts",
        sa.Column(
            "category",
            sa.String(length=100),
            nullable=True,
        ),
    )

    op.add_column(
        "contracts",
        sa.Column(
            "created_by",
            sa.Integer(),
            nullable=True,
        ),
    )

    op.add_column(
        "contracts",
        sa.Column(
            "assigned_to",
            sa.Integer(),
            nullable=True,
        ),
    )

    op.add_column(
        "contracts",
        sa.Column(
            "reviewed_at",
            sa.DateTime(),
            nullable=True,
        ),
    )

    op.add_column(
        "contracts",
        sa.Column(
            "approved_at",
            sa.DateTime(),
            nullable=True,
        ),
    )

    # ---------------------------------------------------------
    # 2. Preserve existing ownership data
    # ---------------------------------------------------------

    # Existing owner becomes the creator.
    #
    # Existing owner also becomes the initial assignee so that
    # the current contract ownership is not lost.
    op.execute(
        """
        UPDATE contracts
        SET
            created_by = owner_id,
            assigned_to = owner_id,
            category = 'Uncategorized'
        """
    )

    # ---------------------------------------------------------
    # 3. Make required columns NOT NULL
    # ---------------------------------------------------------

    op.alter_column(
        "contracts",
        "category",
        existing_type=sa.String(length=100),
        nullable=False,
    )

    op.alter_column(
        "contracts",
        "created_by",
        existing_type=sa.Integer(),
        nullable=False,
    )

    # ---------------------------------------------------------
    # 4. Remove old owner foreign key
    # ---------------------------------------------------------

    op.drop_constraint(
        "contracts_owner_id_fkey",
        "contracts",
        type_="foreignkey",
    )

    # ---------------------------------------------------------
    # 5. Add new foreign keys
    # ---------------------------------------------------------

    op.create_foreign_key(
        "contracts_created_by_fkey",
        "contracts",
        "users",
        ["created_by"],
        ["id"],
        ondelete="RESTRICT",
    )

    op.create_foreign_key(
        "contracts_assigned_to_fkey",
        "contracts",
        "users",
        ["assigned_to"],
        ["id"],
        ondelete="SET NULL",
    )

    # ---------------------------------------------------------
    # 6. Remove old owner index
    # ---------------------------------------------------------

    op.drop_index(
        "ix_contracts_owner_id",
        table_name="contracts",
    )

    # ---------------------------------------------------------
    # 7. Remove old owner column
    # ---------------------------------------------------------

    op.drop_column(
        "contracts",
        "owner_id",
    )

    # ---------------------------------------------------------
    # 8. Contract number indexing
    # ---------------------------------------------------------

    op.drop_constraint(
        "contracts_contract_number_key",
        "contracts",
        type_="unique",
    )

    op.create_index(
        "ix_contracts_contract_number",
        "contracts",
        ["contract_number"],
        unique=True,
    )

    # ---------------------------------------------------------
    # 9. New indexes
    # ---------------------------------------------------------

    op.create_index(
        "ix_contracts_created_by",
        "contracts",
        ["created_by"],
        unique=False,
    )

    op.create_index(
        "ix_contracts_assigned_to",
        "contracts",
        ["assigned_to"],
        unique=False,
    )

    op.create_index(
        "ix_contracts_status",
        "contracts",
        ["status"],
        unique=False,
    )


def downgrade() -> None:
    """
    Reverse the Contract workflow migration.

    created_by is copied back to owner_id.
    """

    # ---------------------------------------------------------
    # 1. Restore owner_id temporarily as nullable
    # ---------------------------------------------------------

    op.add_column(
        "contracts",
        sa.Column(
            "owner_id",
            sa.Integer(),
            nullable=True,
        ),
    )

    # ---------------------------------------------------------
    # 2. Restore previous ownership
    # ---------------------------------------------------------

    op.execute(
        """
        UPDATE contracts
        SET owner_id = created_by
        """
    )

    # ---------------------------------------------------------
    # 3. Make owner_id required
    # ---------------------------------------------------------

    op.alter_column(
        "contracts",
        "owner_id",
        existing_type=sa.Integer(),
        nullable=False,
    )

    # ---------------------------------------------------------
    # 4. Remove new foreign keys
    # ---------------------------------------------------------

    op.drop_constraint(
        "contracts_created_by_fkey",
        "contracts",
        type_="foreignkey",
    )

    op.drop_constraint(
        "contracts_assigned_to_fkey",
        "contracts",
        type_="foreignkey",
    )

    # ---------------------------------------------------------
    # 5. Restore old owner foreign key
    # ---------------------------------------------------------

    op.create_foreign_key(
        "contracts_owner_id_fkey",
        "contracts",
        "users",
        ["owner_id"],
        ["id"],
        ondelete="CASCADE",
    )

    # ---------------------------------------------------------
    # 6. Remove new indexes
    # ---------------------------------------------------------

    op.drop_index(
        "ix_contracts_status",
        table_name="contracts",
    )

    op.drop_index(
        "ix_contracts_assigned_to",
        table_name="contracts",
    )

    op.drop_index(
        "ix_contracts_created_by",
        table_name="contracts",
    )

    op.drop_index(
        "ix_contracts_contract_number",
        table_name="contracts",
    )

    # ---------------------------------------------------------
    # 7. Restore original contract-number constraint
    # ---------------------------------------------------------

    op.create_unique_constraint(
        "contracts_contract_number_key",
        "contracts",
        ["contract_number"],
    )

    # ---------------------------------------------------------
    # 8. Restore owner index
    # ---------------------------------------------------------

    op.create_index(
        "ix_contracts_owner_id",
        "contracts",
        ["owner_id"],
        unique=False,
    )

    # ---------------------------------------------------------
    # 9. Remove new columns
    # ---------------------------------------------------------

    op.drop_column(
        "contracts",
        "approved_at",
    )

    op.drop_column(
        "contracts",
        "reviewed_at",
    )

    op.drop_column(
        "contracts",
        "assigned_to",
    )

    op.drop_column(
        "contracts",
        "created_by",
    )

    op.drop_column(
        "contracts",
        "category",
    )