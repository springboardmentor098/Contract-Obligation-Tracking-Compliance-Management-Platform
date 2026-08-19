"""add contract workflow fields

Revision ID: a02d01ca2bde
Revises: 14ff857e3d92
Create Date: 2026-08-19 17:19:07.131921

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a02d01ca2bde"
down_revision: Union[str, Sequence[str], None] = "14ff857e3d92"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # ============================================================
    # ADD CONTRACT ASSIGNMENT
    # ============================================================

    op.add_column(
        "contracts",
        sa.Column(
            "assigned_to",
            sa.Integer(),
            nullable=True
        )
    )

    # ============================================================
    # ADD WORKFLOW TIMESTAMPS
    # ============================================================

    op.add_column(
        "contracts",
        sa.Column(
            "reviewed_at",
            sa.DateTime(),
            nullable=True
        )
    )

    op.add_column(
        "contracts",
        sa.Column(
            "approved_at",
            sa.DateTime(),
            nullable=True
        )
    )

    # ============================================================
    # ASSIGNED USER FOREIGN KEY
    # ============================================================

    op.create_foreign_key(
        "fk_contracts_assigned_to_users",
        "contracts",
        "users",
        ["assigned_to"],
        ["id"]
    )


def downgrade() -> None:
    """Downgrade schema."""

    # Remove foreign key
    op.drop_constraint(
        "fk_contracts_assigned_to_users",
        "contracts",
        type_="foreignkey"
    )

    # Remove workflow fields
    op.drop_column(
        "contracts",
        "approved_at"
    )

    op.drop_column(
        "contracts",
        "reviewed_at"
    )

    # Remove assignment
    op.drop_column(
        "contracts",
        "assigned_to"
    )