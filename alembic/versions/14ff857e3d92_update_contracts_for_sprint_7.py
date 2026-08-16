"""update contracts for sprint 7

Revision ID: 14ff857e3d92
Revises: 98d23cd8b0ae
Create Date: 2026-08-16
"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "14ff857e3d92"
down_revision = "98d23cd8b0ae"
branch_labels = None
depends_on = None


def upgrade() -> None:

    # ============================================================
    # 1. Rename owner_id -> created_by
    # ============================================================

    op.alter_column(
        "contracts",
        "owner_id",
        new_column_name="created_by"
    )

    # ============================================================
    # 2. Add category temporarily as nullable
    # ============================================================

    op.add_column(
        "contracts",
        sa.Column(
            "category",
            sa.String(length=100),
            nullable=True
        )
    )

    # ============================================================
    # 3. Add timestamps temporarily as nullable
    # ============================================================

    op.add_column(
        "contracts",
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=True
        )
    )

    op.add_column(
        "contracts",
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=True
        )
    )

    # ============================================================
    # 4. Give existing contracts a category
    #
    # Existing contracts were created before category existed.
    # We use "Service Agreement" as the initial category.
    # ============================================================

    op.execute(
        """
        UPDATE contracts
        SET category = 'Service Agreement'
        WHERE category IS NULL
        """
    )

    # ============================================================
    # 5. Populate timestamps for existing contracts
    # ============================================================

    op.execute(
        """
        UPDATE contracts
        SET
            created_at = CURRENT_TIMESTAMP,
            updated_at = CURRENT_TIMESTAMP
        WHERE created_at IS NULL
           OR updated_at IS NULL
        """
    )

    # ============================================================
    # 6. Make new fields mandatory
    # ============================================================

    op.alter_column(
        "contracts",
        "category",
        nullable=False
    )

    op.alter_column(
        "contracts",
        "created_at",
        nullable=False
    )

    op.alter_column(
        "contracts",
        "updated_at",
        nullable=False
    )


def downgrade() -> None:

    # ============================================================
    # Reverse Sprint 7 changes
    # ============================================================

    op.drop_column(
        "contracts",
        "updated_at"
    )

    op.drop_column(
        "contracts",
        "created_at"
    )

    op.drop_column(
        "contracts",
        "category"
    )

    op.alter_column(
        "contracts",
        "created_by",
        new_column_name="owner_id"
    )