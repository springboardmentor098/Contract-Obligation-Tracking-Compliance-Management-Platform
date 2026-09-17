"""add contract workflow fields

Revision ID: e1c3690e562b
Revises: aec4f2355626
Create Date: 2026-08-19 18:43:44.179526

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "e1c3690e562b"
down_revision: Union[str, Sequence[str], None] = "aec4f2355626"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    # Add contract assignment field
    op.add_column(
        "contracts",
        sa.Column(
            "assigned_to",
            sa.Integer(),
            nullable=True
        )
    )

    # Add workflow timestamp fields
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

    # Link assigned_to to users.id
    op.create_foreign_key(
        "fk_contracts_assigned_to_users",
        "contracts",
        "users",
        ["assigned_to"],
        ["id"]
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_constraint(
        "fk_contracts_assigned_to_users",
        "contracts",
        type_="foreignkey"
    )

    op.drop_column(
        "contracts",
        "approved_at"
    )

    op.drop_column(
        "contracts",
        "reviewed_at"
    )

    op.drop_column(
        "contracts",
        "assigned_to"
    )