"""add document_url to contracts

Revision ID: 8c2d4a9f1b2a
Revises: 1a6b791ffdcd
Create Date: 2026-09-18 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '8c2d4a9f1b2a'
down_revision: Union[str, Sequence[str], None] = '1a6b791ffdcd'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column('contracts', sa.Column('document_url', sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column('contracts', 'document_url')
