"""rename owner_id to created_by

Revision ID: aec4f2355626
Revises: 414d08a4af04
Create Date: 2026-08-14 21:22:19.082047

"""
from typing import Sequence, Union

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "aec4f2355626"
down_revision: Union[str, Sequence[str], None] = "414d08a4af04"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Rename owner_id column to created_by."""

    op.alter_column(
        "contracts",
        "owner_id",
        new_column_name="created_by"
    )


def downgrade() -> None:
    """Rename created_by column back to owner_id."""

    op.alter_column(
        "contracts",
        "created_by",
        new_column_name="owner_id"
    )