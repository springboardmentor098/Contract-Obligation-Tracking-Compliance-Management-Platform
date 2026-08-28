"""add obligation workflow fields

Revision ID: 1ff81a4bff3a
Revises: a2b36972b615
Create Date: 2026-08-23 13:03:27.001817

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1ff81a4bff3a'
down_revision: Union[str, Sequence[str], None] = 'a2b36972b615'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""

    op.add_column(
        'obligations',
        sa.Column(
            'completion_date',
            sa.Date(),
            nullable=True
        )
    )

    op.add_column(
        'obligations',
        sa.Column(
            'created_at',
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now()
        )
    )

    op.add_column(
        'obligations',
        sa.Column(
            'updated_at',
            sa.DateTime(),
            nullable=False,
            server_default=sa.func.now()
        )
    )


def downgrade() -> None:
    """Downgrade schema."""

    op.drop_column('obligations', 'updated_at')
    op.drop_column('obligations', 'created_at')
    op.drop_column('obligations', 'completion_date')