"""add password column

Revision ID: a86d3f36280f
Revises: ac38f3e2fe13
Create Date: 2026-08-06 18:53:15.769246

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "a86d3f36280f"
down_revision: Union[str, Sequence[str], None] = "ac38f3e2fe13"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "users",
        sa.Column("password", sa.String(length=255), nullable=True)
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("users", "password")