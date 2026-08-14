"""update contracts table for sprint 7

Revision ID: 79e85c3f6b6f
Revises: 84b09865b673
Create Date: 2026-08-14

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "79e85c3f6b6f"
down_revision: Union[str, Sequence[str], None] = "84b09865b673"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Add Sprint 7 columns
    op.add_column(
        "contracts",
        sa.Column(
            "category",
            sa.String(),
            nullable=False,
            server_default="Vendor Contract"
        )
    )

    op.add_column(
        "contracts",
        sa.Column(
            "created_by",
            sa.Integer(),
            nullable=False
        )
    )

    op.add_column(
        "contracts",
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP")
        )
    )

    op.add_column(
        "contracts",
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP")
        )
    )

    # Remove old owner foreign key
    op.drop_constraint(
        "contracts_owner_id_fkey",
        "contracts",
        type_="foreignkey"
    )

    # Add new created_by foreign key
    op.create_foreign_key(
        "contracts_created_by_fkey",
        "contracts",
        "users",
        ["created_by"],
        ["id"]
    )

    # Remove old owner_id column
    op.drop_column(
        "contracts",
        "owner_id"
    )


def downgrade() -> None:
    # Restore owner_id
    op.add_column(
        "contracts",
        sa.Column(
            "owner_id",
            sa.Integer(),
            nullable=False
        )
    )

    # Remove created_by foreign key
    op.drop_constraint(
        "contracts_created_by_fkey",
        "contracts",
        type_="foreignkey"
    )

    # Restore owner_id foreign key
    op.create_foreign_key(
        "contracts_owner_id_fkey",
        "contracts",
        "users",
        ["owner_id"],
        ["id"]
    )

    # Remove Sprint 7 columns
    op.drop_column("contracts", "updated_at")
    op.drop_column("contracts", "created_at")
    op.drop_column("contracts", "created_by")
    op.drop_column("contracts", "category")