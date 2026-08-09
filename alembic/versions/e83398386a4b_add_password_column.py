"""add password column

Revision ID: e83398386a4b
Revises: d3a4adab757b
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "e83398386a4b"
down_revision: Union[str, Sequence[str], None] = "d3a4adab757b"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "users",
        sa.Column(
            "password",
            sa.String(),
            nullable=False
        )
    )


def downgrade() -> None:
    op.drop_column(
        "users",
        "password"
    )