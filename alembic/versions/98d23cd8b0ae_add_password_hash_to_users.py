"""add password hash to users

Revision ID: 98d23cd8b0ae
Revises: b49f4f715021
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "98d23cd8b0ae"
down_revision: Union[str, Sequence[str], None] = "b49f4f715021"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    # 1. Add password_hash temporarily as nullable
    op.add_column(
        "users",
        sa.Column(
            "password_hash",
            sa.String(length=255),
            nullable=True
        )
    )

    # 2. Set a temporary password hash for existing users
    op.execute(
        """
        UPDATE users
        SET password_hash = '$2b$12$CcVmFkJOw7rLf/szeU6LAemHA4lP.Kn0IUCsqAdZBqxDY8vU.HezK'
        WHERE password_hash IS NULL
        """
    )

    # 3. Make password_hash mandatory
    op.alter_column(
        "users",
        "password_hash",
        existing_type=sa.String(length=255),
        nullable=False
    )


def downgrade() -> None:

    op.drop_column(
        "users",
        "password_hash"
    )